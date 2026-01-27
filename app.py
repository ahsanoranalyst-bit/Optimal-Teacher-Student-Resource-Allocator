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
        grade_data = pd.DataFrame({
            "Grade Level": ["Lower Primary (1-5)", "Upper Primary (6-8)", "Secondary (9-12)"],
            "General Students": [400, 320, 250],
            "Special Needs (SN)": [35, 20, 15]
        })
        input_grades = st.data_editor(grade_data, use_container_width=True, key="grade_input")
    
    with col_a2:
        sn_weight = st.slider("SN Workload Multiplier", 1.0, 3.0, 2.0, 
                              help="Weight of one SN student vs one General student.")

    weighted_load = input_grades["General Students"].sum() + (input_grades["Special Needs (SN)"].sum() * sn_weight)
    st.info(f"**Total Calculated Workload Units:** {weighted_load}")

st.write("---")

# =========================================================
# SECTION B: TEACHER PROFILE (INTERNAL PERFORMANCE)
# =========================================================
st.header("🧑‍🏫 Section B: Teacher Profile & Metrics")
st.markdown("Enter core staff qualifications and historical performance data.")
with st.container():
    # Base Data
    initial_b_data = pd.DataFrame({
        "Teacher Name": ["Aris", "Bo", "Cy", "Di", "El"],
        "Qualification": ["PhD", "Masters", "Masters", "Bachelors", "Masters"],
        "Seniority (Years)": [15, 8, 5, 2, 10],
        "Performance Metric": [9.6, 8.2, 7.5, 9.3, 8.7]
    })
    # Editable Dataframe
    edited_b_df = st.data_editor(initial_b_data, num_rows="dynamic", use_container_width=True, key="prof_editor")

st.write("---")

# =========================================================
# SECTION C: EFFICIENCY (CONSTRAINTS)
# =========================================================
st.header("⚙️ Section C: Efficiency & Capacity")
with st.container():
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        target_ratio = st.number_input("Target Student-to-Teacher Ratio", 10, 50, 25)
    with col_c2:
        admin_hours = st.slider("Weekly Administrative Burden (Hours)", 0, 25, 6)

    # Calculation logic
    efficiency = (40 - admin_hours) / 40
    opt_staff = np.ceil((weighted_load / target_ratio) / efficiency)

st.write("---")

# =========================================================
# SECTION D: FEEDBACK (EXTERNAL QUALITY)
# =========================================================
st.header("💬 Section D: Feedback & Satisfaction Scores")
st.markdown("Input data from Student Surveys and Peer Evaluations.")
with st.container():
    # Sync names from Section B to ensure data integrity
    names_from_b = edited_b_df["Teacher Name"].tolist()
    
    # Pre-fill feedback data based on current staff list
    initial_d_data = pd.DataFrame({
        "Teacher Name": names_from_b,
        "Student Satisfaction %": [90] * len(names_from_b),
        "Peer Review (1-5)": [4.0] * len(names_from_b)
    })
    
    # Map old values if names exist to prevent data loss on every edit
    feedback_df = st.data_editor(initial_d_data, use_container_width=True, key="feedback_editor")

st.write("---")

# =========================================================
# FINAL OPTIMIZATION ENGINE
# =========================================================
st.header("🚀 Strategic Staffing Optimization")

# 1. Merge Internal (B) and External (D) Data
combined_stats = pd.merge(edited_b_df, feedback_df, on="Teacher Name")

# 2. Logic: Multi-Objective Capability Index
# We normalize scales to a 0.0 - 1.0 range for fair weighting
combined_stats['Capability_Score'] = (
    (combined_stats['Performance Metric'] / 10 * 0.4) +        # 40% Internal Performance
    (combined_stats['Student Satisfaction %'] / 100 * 0.3) +  # 30% Student Feedback
    (combined_stats['Peer Review (1-5)'] / 5 * 0.2) +         # 20% Peer Review
    (np.log1p(combined_stats['Seniority (Years)']) / 3 * 0.1) # 10% Seniority (Diminishing returns)
)

final_rank = combined_stats.sort_values(by="Capability_Score", ascending=False)

# 3. Results Display
col_res1, col_res2 = st.columns([1, 2])

with col_res1:
    st.metric("Optimal Staff Required", f"{int(opt_staff)} Teachers")
    st.metric("Current Staff Count", len(edited_b_df))
    
    gap = int(opt_staff - len(edited_b_df))
    if gap > 0:
        st.warning(f"⚠️ Staffing Shortage: +{gap} needed")
    else:
        st.success("✅ Staffing Levels Optimal")

with col_res2:
    fig = px.bar(final_rank, x="Teacher Name", y="Capability_Score", 
                 color="Capability_Score", title="Total Capability Mapping",
                 color_continuous_
