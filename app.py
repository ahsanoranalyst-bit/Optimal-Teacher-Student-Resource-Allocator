import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# PAGE LAYOUT SETUP
st.set_page_config(page_title="Optimal Resource Allocator", layout="wide")

st.title("⚖️ Optimal Teacher-Student Resource Allocator")
st.markdown("### Operations Research & Staffing Optimization Dashboard")
st.divider()

# =========================================================
# SECTION A: STUDENT LOAD (Demand Analysis)
# =========================================================
st.header("📂 Section A: Student Load Profile")
col_a1, col_a2 = st.columns([2, 1])

with col_a1:
    # Requirement: Grade-wise student count and Special Needs
    grade_data = pd.DataFrame({
        "Grade Level": ["Lower Primary (1-5)", "Upper Primary (6-8)", "Secondary (9-12)"],
        "General Enrollment": [350, 280, 220],
        "Special Needs (SN)": [30, 18, 12]
    })
    input_grades = st.data_editor(grade_data, use_container_width=True, key="grade_input")

with col_a2:
    sn_multiplier = st.select_slider(
        "SN Complexity Weight",
        options=[1.0, 1.5, 2.0, 2.5, 3.0],
        value=2.0,
        help="How many 'standard' student slots one SN student consumes."
    )

# LOGIC A: Calculate Weighted System Workload
gen_total = input_grades["General Enrollment"].sum()
sn_total = input_grades["Special Needs (SN)"].sum()
weighted_load = gen_total + (sn_total * sn_multiplier)
st.info(f"**Calculated Total Workload Units:** {weighted_load}")

st.divider()

# =========================================================
# SECTION B: TEACHER PROFILE (Internal Quality)
# =========================================================
st.header("🧑‍🏫 Section B: Teacher Profiles")
# Requirement: Qualification, Seniority, Past performance metrics
b_data = pd.DataFrame({
    "Teacher Name": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
    "Qualification": ["PhD", "Masters", "Masters", "Bachelors", "Masters"],
    "Seniority (Years)": [14, 7, 5, 2, 11],
    "Performance (1-10)": [9.6, 8.3, 7.8, 9.2, 8.7]
})
st.dataframe(b_data, use_container_width=True)

st.divider()

# =========================================================
# SECTION C: EFFICIENCY (Capacity Constraints)
# =========================================================
st.header("⚙️ Section C: Efficiency Constraints")
col_c1, col_c2 = st.columns(2)

with col_c1:
    target_ratio = st.number_input("Target Student-Teacher Ratio", 10, 40, 22)
with col_c2:
    admin_burden = st.slider("Weekly Admin/Task Hours", 0, 25, 6)

# LOGIC C: System Efficiency Optimization
# Treats admin hours as 'leakage' from the 40-hour teaching capacity
efficiency_factor = (40 - admin_burden) / 40
opt_staff_required = np.ceil((weighted_load / target_ratio) / efficiency_factor)

st.divider()

# =========================================================
# SECTION D: FEEDBACK (External Quality)
# =========================================================
st.header("💬 Section D: Feedback & Satisfaction")
# Requirement: Student satisfaction scores, Peer review data
d_data = pd.DataFrame({
    "Teacher Name": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
    "Student Satisfaction (%)": [98, 87, 82, 94, 89],
    "Peer Review (1-5)": [4.9, 4.2, 3.7, 4.6, 4.2]
})
st.dataframe(d_data, use_container_width=True)

st.divider()

# =========================================================
# FINAL OPTIMIZATION OUTPUT
# =========================================================
st.header("🚀 Strategic Optimization Result")

# Merge B and D to create the Knowledge-Capability Index
full_analytics = pd.merge(b_data, d_data, on="Teacher Name")

# Optimization Calculation: Composite Capability Score
full_analytics['Capability_Index'] = (
    (full_analytics['Performance (1-10)'] * 0.4) +
    ((full_analytics['Student Satisfaction (%)'] / 10) * 0.3) +
    ((full_analytics['Peer Review (1-5)'] * 2) * 0.2) +
    (np.log1p(full_analytics['Seniority (Years)']) * 0.1)
)

final_ranking = full_analytics.sort_values(by='Capability_Index', ascending=False)

res_col1, res_col2, res_col3 = st.columns(3)
res_col1.metric("Optimal Staff Needed", f"{int(opt_staff_needed)} FTEs")
res_col2.metric("Total Weighted Load", f"{int(weighted_load)}")
res_col3.metric("System Efficiency", f"{efficiency_factor*100:.1f}%")

# VISUALIZATION
st.subheader("Teacher Capability vs. Seniority (Optimization Map)")
fig = px.scatter(final_ranking, x="Seniority (Years)", y="Capability_Index", 
                 size="Performance (1-10)", color="Teacher Name", 
                 text="Teacher Name", hover_name="Qualification")
st.plotly_chart(fig, use_container_width=True)

st.success(f"**Final Recommendation:** Based on current metrics, you require **{int(opt_staff_needed)}** staff members. To optimize educational quality, deploy **{final_ranking.iloc[0]['Teacher Name']}** to the most complex student clusters identified in Section A.")
