import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Optimal Resource Allocator", layout="wide")

st.title("⚖️ Optimal Teacher-Student Resource Allocator")
st.markdown("### Strategic Operations Research & Staffing Optimization")
st.write("---")

# =========================================================
# SECTION A: STUDENT LOAD (DEMAND)
# =========================================================
st.header("📂 Section A: Student Load Profile")
with st.container():
    col_a1, col_a2 = st.columns([2, 1])
    with col_a1:
        # User inputs Grade-wise counts
        grade_data = pd.DataFrame({
            "Grade Level": ["Lower Primary (1-5)", "Upper Primary (6-8)", "Secondary (9-12)"],
            "General Students": [400, 320, 250],
            "Special Needs (SN)": [35, 20, 15]
        })
        input_grades = st.data_editor(grade_data, use_container_width=True, key="grade_input")
    
    with col_a2:
        sn_weight = st.slider("SN Workload Multiplier", 1.0, 3.0, 2.0, 
                              help="Weight of one SN student vs one General student (e.g., 2.0 means 1 SN student equals 2 General students).")

    # LOGIC A: Calculate Weighted System Workload
    total_gen = input_grades["General Students"].sum()
    total_sn = input_grades["Special Needs (SN)"].sum()
    weighted_load = total_gen + (total_sn * sn_weight)
    
    st.info(f"**Total Weighted Load:** {weighted_load} Units")

st.write("---")

# =========================================================
# SECTION B: TEACHER PROFILE (INTERNAL DATA)
# =========================================================
st.header("🧑‍🏫 Section B: Teacher Profile & Performance")
with st.container():
    # Requirement: Qualification, Seniority, Past Performance
    initial_b_data = pd.DataFrame({
        "Teacher Name": ["Aris", "Bo", "Cy", "Di", "El"],
        "Qualification": ["PhD", "Masters", "Masters", "Bachelors", "Masters"],
        "Seniority (Years)": [15, 8, 5, 2, 10],
        "Past Performance (1-10)": [9.6, 8.2, 7.5, 9.3, 8.7]
    })
    edited_b = st.data_editor(initial_b_data, use_container_width=True, num_rows="dynamic", key="sec_b")

st.write("---")

# =========================================================
# SECTION C: EFFICIENCY (CONSTRAINTS)
# =========================================================
st.header("⚙️ Section C: Efficiency & Capacity")
with st.container():
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        target_ratio = st.number_input("Target Teacher-Student Ratio (1:X)", 5, 50, 22)
    with col_c2:
        admin_hours = st.slider("Weekly Administrative Task Hours", 0, 20, 4)

    # LOGIC C: Adjust capacity based on admin burden
    # Assuming a 40-hour standard work week
    efficiency_factor = (40 - admin_hours) / 40
    required_staff = np.ceil((weighted_load / target_ratio) / efficiency_factor)

st.write("---")

# =========================================================
# SECTION D: FEEDBACK (EXTERNAL QUALITY)
# =========================================================
st.header("💬 Section D: Feedback & Satisfaction")
with st.container():
    # Sync with Section B names to ensure logic consistency
    current_names = edited_b["Teacher Name"].tolist()
    
    # Requirement: Student Satisfaction + Peer Review
    d_template = pd.DataFrame({
        "Teacher Name": current_names,
        "Student Satisfaction %": [92, 85, 78, 95, 88][:len(current_names)] if len(current_names) <= 5 else [85]*len(current_names),
        "Peer Review (1-5)": [4.8, 4.0, 3.8, 4.6, 4.2][:len(current_names)] if len(current_names) <= 5 else [4.0]*len(current_names)
    })
    edited_d = st.data_editor(d_template, use_container_width=True, key="sec_d")

st.write("---")

# =========================================================
# FINAL OPTIMIZATION & COMBINED LOGIC
# =========================================================
st.header("🚀 Optimal Allocation Result")

# 1. Merge all data for logic combining
combined_df = pd.merge(edited_b, edited_d, on="Teacher Name")

# 2. Optimization Logic: Capability Index Calculation
# We combine metrics into a single score out of 100
combined_df['Capability_Index'] = (
    (combined_df['Past Performance (1-10)'] * 4) +           # 40% Weight
    (combined_df['Student Satisfaction %'] * 0.3) +          # 30% Weight
    (combined_df['Peer Review (1-5)'] * 4) +                 # 20% Weight
    (np.log1p(combined_df['Seniority (Years)']) * 2)         # 10% Weight (Log used for diminishing returns)
)

final_rank = combined_df.sort_values(by="Capability_Index", ascending=False)

# 3. Visualizations & Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Current Staff", len(edited_b))
m2.metric("Required Staff", int(required_staff))
m3.metric("Staff Gap", int(required_staff - len(edited_b)))

# Radar-style capability visualization
fig = px.bar(final_rank, x="Teacher Name", y="Capability_Index", 
             color="Capability_Index", title="Total Capability Ranking",
             color_continuous_scale="Viridis")
st.plotly_chart(fig, use_container_width=True)

# 4. Final Strategic Summary
st.success(f"**Optimization Summary:** To meet your target ratio of 1:{target_ratio} under current admin burdens, you require **{int(required_staff)}** teachers. Based on the integrated Capability Index, **{final_rank.iloc[0]['Teacher Name']}** is identified as your highest-performing asset for complex allocations.")
