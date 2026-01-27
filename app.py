import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Optimal Resource Allocator", layout="wide")
st.title("⚖️ Optimal Teacher-Student Resource Allocator")
st.markdown("---")

# =========================================================
# SECTION A: STUDENT LOAD (Demand Modeling)
# =========================================================
st.header("📂 Section A: Student Load Profile")
with st.container():
    col_a1, col_a2 = st.columns([2, 1])
    with col_a1:
        # Input for Grade-wise student counts
        grade_data = pd.DataFrame({
            "Grade Level": ["Grade 1-5", "Grade 6-8", "Grade 9-12"],
            "General Students": [350, 280, 220],
            "Special Needs Students": [30, 18, 12]
        })
        input_grades = st.data_editor(grade_data, use_container_width=True, key="grades")
    
    with col_a2:
        sn_weight = st.select_slider(
            "Special Needs Complexity Weight",
            options=[1.0, 1.5, 2.0, 2.5, 3.0],
            value=2.0,
            help="Defines the workload ratio of 1 SN student compared to a General student."
        )

    # Logic A: Calculate Weighted Demand
    total_gen = input_grades["General Students"].sum()
    total_sn = input_grades["Special Needs Students"].sum()
    weighted_workload = total_gen + (total_sn * sn_weight)
    st.info(f"**Calculated System Workload Units:** {weighted_workload}")

st.markdown("---")

# =========================================================
# SECTION B: TEACHER PROFILE (Supply - Internal)
# =========================================================
st.header("🧑‍🏫 Section B: Teacher Profile & Metrics")
with st.container():
    # Includes Qualification, Seniority, and Performance scores
    teacher_profiles = pd.DataFrame({
        "Teacher Name": ["Mx. Alpha", "Mx. Beta", "Mx. Gamma", "Mx. Delta", "Mx. Epsilon"],
        "Qualification": ["PhD", "Masters", "Masters", "Bachelors", "Masters"],
        "Seniority (Years)": [14, 7, 5, 2, 10],
        "Performance Metric (1-10)": [9.6, 8.3, 7.8, 9.2, 8.7]
    })
    st.table(teacher_profiles)

st.markdown("---")

# =========================================================
# SECTION C: EFFICIENCY (System Friction)
# =========================================================
st.header("⚙️ Section C: Efficiency & Capacity Constraints")
with st.container():
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        target_ratio = st.number_input("Target Student-Teacher Ratio", 10, 40, 22)
    with col_c2:
        admin_hours = st.slider("Weekly Administrative Burden (Hours)", 0, 25, 6)

    # Logic C: Capacity Constraint calculation
    efficiency_factor = (40 - admin_hours) / 40
    opt_staff_needed = np.ceil((weighted_workload / target_ratio) / efficiency_factor)

st.markdown("---")

# =========================================================
# SECTION D: FEEDBACK (Supply - External)
# =========================================================
st.header("💬 Section D: Feedback & Satisfaction Data")
with st.container():
    # Includes Satisfaction and Peer Review metrics
    feedback_data = pd.DataFrame({
        "Teacher Name": ["Mx. Alpha", "Mx. Beta", "Mx. Gamma", "Mx. Delta", "Mx. Epsilon"],
        "Student Satisfaction (%)": [98, 87, 82, 94, 89],
        "Peer Review Score (1-5)": [4.9, 4.2, 3.7, 4.6, 4.1]
    })
    st.table(feedback_data)

st.markdown("---")

# =========================================================
# FINAL OPTIMIZATION ENGINE (MCDA)
# =========================================================
st.header("🚀 Strategic Optimization Analysis")

# Merge Supply Sections (B & D)
combined_df = pd.merge(teacher_profiles, feedback_data, on="Teacher Name")

# OR ANALYST LOGIC: Creating the Capability Index
# Formula: (Perf*0.4) + (Sat/10 * 0.3) + (Peer*2 * 0.2) + (log(Seniority) * 0.1)
combined_df['Capability_Index'] = (
    (combined_df['Performance Metric (1-10)'] * 0.4) +
    ((combined_df['Student Satisfaction (%)'] / 10) * 0.3) +
    ((combined_df['Peer Review Score (1-5)'] * 2) * 0.2) +
    (np.log1p(combined_df['Seniority (Years)']) * 0.1)
)

final_ranking = combined_df.sort_values(by="Capability_Index", ascending=False)

# Display Key Result Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Optimal Staff Required", f"{int(opt_staff_needed)} Teachers")
m2.metric("Total System Load", f"{int(weighted_workload)}")
m3.metric("Top Talent Lead", final_ranking.iloc[0]['Teacher Name'])

# Optimization Visualization
fig = px.bar(final_ranking, x="Teacher Name", y="Capability_Index", 
             color="Capability_Index", text_auto='.2f',
             title="Teacher Knowledge-Capability Ranking")
st.plotly_chart(fig, use_container_width=True)

st.success(f"**Optimization Summary:** Based on the efficiency constraints in Section C, a minimum of **{int(opt_staff_needed)}** staff members are required. To maximize educational outcomes, we recommend **{final_ranking.iloc[0]['Teacher Name']}** for high-complexity groups identified in Section A.")
