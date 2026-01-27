import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
st.markdown("Edit teacher seniority and internal performance ratings below.")
with st.container():
    # Base internal data
    b_data = pd.DataFrame({
        "Teacher Name": ["Aris", "Bo", "Cy", "Di", "El"],
        "Qualification": ["PhD", "Masters", "Masters", "Bachelors", "Masters"],
        "Seniority (Years)": [15, 8, 5, 2, 10],
        "Performance Metric": [9.6, 8.2, 7.5, 9.3, 8.7]
    })
    # Allowing dynamic editing of the internal profile
    edited_b_data = st.data_editor(b_data, use_container_width=True, num_rows="dynamic", key="editor_b")

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

    # Calculation: Efficiency determines how many 'effective' teachers you actually have
    efficiency = (40 - admin_hours) / 40
    opt_staff_req = np.ceil((weighted_load / target_ratio) / efficiency)
    current_staff_count = len(edited_b_data)

st.write("---")

# =========================================================
# SECTION D: FEEDBACK (EXTERNAL QUALITY)
# =========================================================
st.header("💬 Section D: Feedback & Satisfaction Scores")
st.markdown("Input qualitative data from student surveys and peer reviews.")
with st.container():
    # We map Section D to the names currently in Section B to ensure consistency
    d_data_template = pd.DataFrame({
        "Teacher Name": edited_b_data["Teacher Name"],
        "Student Satisfaction %": [98, 85, 80, 95, 88][:len(edited_b_data)] if len(edited_b_data) <= 5 else [85]*len(edited_b_data),
        "Peer Review (1-5)": [4.9, 4.1, 3.5, 4.7, 4.2][:len(edited_b_data)] if len(edited_b_data) <= 5 else [4.0]*len(edited_b_data)
    })
    edited_d_data = st.data_editor(d_data_template, use_container_width=True, key="editor_d")

st.write("---")

# =========================================================
# FINAL OPTIMIZATION ENGINE
# =========================================================
st.header("🚀 Strategic Staffing Optimization")

# Merge Section B (Internal) and Section D (External)
combined_df = pd.merge(edited_b_data, edited_d_data, on="Teacher Name")

# Optimization Logic: Weighted Capability Index (0-10 Scale)
combined_df['Capability_Index'] = (
    (combined_df['Performance Metric'] * 0.4) +           # 40% Weight: Internal KPI
    ((combined_df['Student Satisfaction %'] / 10) * 0.3) + # 30% Weight: Student Feedback
    ((combined_df['Peer Review (1-5)'] * 2) * 0.2) +      # 20% Weight: Peer Review
    (np.log1p(combined_df['Seniority (Years)']) * 0.1)    # 10% Weight: Experience
)

final_rank = combined_df.sort_values(by="Capability_Index", ascending=False)

# Results Display - Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Optimal Staff Required", f"{int(opt_staff_req)} Teachers")
m2.metric("Current Staff Count", f"{current_staff_count}")
m3.metric("Staffing Gap", f"{int(opt_staff_req - current_staff_count)}")

# Visualizing the Capability Portfolio
st.subheader("📊 Knowledge-Capability Mapping")
fig = px.bar(
    final_rank, 
    x="Teacher Name", 
    y="Capability_Index", 
    color="Capability_Index",
    text_auto='.2f',
    title="Combined Teacher Ranking (Internal + External Metrics)",
    color_continuous_scale="RdYlGn"
)
st.plotly_chart(fig, use_container_width=True)

# Final Summary Recommendation
top_teacher = final_rank.iloc[0]["Teacher Name"]
st.success(f"""
**Optimization Summary:**
* To maintain a **{target_ratio}:1** ratio with **{admin_hours}h** admin burden, you require **{int(opt_staff_req)}** total staff.
* Currently, you have a gap of **{int(opt_staff_req - current_staff_count)}** teachers.
* **Top Talent Recommendation:** We recommend assigning **{top_teacher}** to lead high-priority or high-load clusters.
""")
