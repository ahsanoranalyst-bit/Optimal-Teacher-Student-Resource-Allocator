import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set page to wide mode so all sections are visible
st.set_page_config(page_title="Strategic Resource Allocator", layout="wide")

st.title("⚖️ Optimal Teacher-Student Resource Allocator")
st.markdown("### Unified Optimization Dashboard (Sections A, B, C, & D)")
st.write("---")

# ==========================================
# SECTION A: STUDENT LOAD (Demand)
# ==========================================
st.header("📂 Section A: Student Load Profile")
with st.container():
    col_a1, col_a2 = st.columns([2, 1])
    with col_a1:
        # User input for Grade-wise distribution
        grade_data = pd.DataFrame({
            "Grade Level": ["Grade 1-5", "Grade 6-8", "Grade 9-12"],
            "General Count": [400, 300, 200],
            "Special Needs (SN) Count": [35, 20, 10]
        })
        input_grades = st.data_editor(grade_data, use_container_width=True, key="grade_editor")
    
    with col_a2:
        sn_multiplier = st.slider("SN Workload Weight", 1.0, 3.0, 2.0)
        
    # Logic A: Weighted Load Calculation
    total_gen = input_grades["General Count"].sum()
    total_sn = input_grades["Special Needs (SN) Count"].sum()
    weighted_load = total_gen + (total_sn * sn_multiplier)
    st.info(f"**Total Weighted Workload Units:** {weighted_load}")

st.write("---")

# ==========================================
# SECTION B: TEACHER PROFILE (Internal Supply)
# ==========================================
st.header("🧑‍🏫 Section B: Teacher Profile & Metrics")
with st.container():
    # Data including Qualification, Seniority, and Performance
    teacher_profiles = pd.DataFrame({
        "Teacher Name": ["Aris", "Bo", "Cy", "Di", "El"],
        "Qualification": ["PhD", "Masters", "Masters", "BA", "MA"],
        "Seniority (Years)": [15, 8, 5, 2, 10],
        "Performance Score": [9.5, 8.2, 7.5, 9.1, 8.8]
    })
    st.table(teacher_profiles)

st.write("---")

# ==========================================
# SECTION C: EFFICIENCY (Constraints)
# ==========================================
st.header("⚙️ Section C: Efficiency & Capacity")
with st.container():
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        target_ratio = st.number_input("Target Student-Teacher Ratio", 10, 50, 22)
    with col_c2:
        admin_hours = st.slider("Weekly Admin Hours per Teacher", 0, 20, 6)

    # Logic C: Efficiency Factor
    efficiency = (40 - admin_hours) / 40
    opt_staff = np.ceil((weighted_load / target_ratio) / efficiency)

st.write("---")

# ==========================================
# SECTION D: FEEDBACK (External Supply)
# ==========================================
st.header("💬 Section D: Feedback & Satisfaction")
with st.container():
    # Data including Student Satisfaction and Peer Reviews
    feedback_data = pd.DataFrame({
        "Teacher Name": ["Aris", "Bo", "Cy", "Di", "El"],
        "Student Satisfaction %": [98, 85, 80, 92, 89],
        "Peer Review (1-5)": [4.9, 4.1, 3.6, 4.7, 4.3]
    })
    st.table(feedback_data)

st.write("---")

# ==========================================
# FINAL OPTIMIZATION ENGINE
# ==========================================
st.header("🚀 Strategic Optimization Result")

# Merge B and D for Capability Index
combined_df = pd.merge(teacher_profiles, feedback_data, on="Teacher Name")

# OR Logic: Capability = (Perf*0.4) + (Sat*0.3) + (Peer*0.2) + (Seniority*0.1)
combined_df['Capability_Index'] = (
    (combined_df['Performance Score'] * 0.4) +
    ((combined_df['Student Satisfaction %'] / 10) * 0.3) +
    ((combined_df['Peer Review (1-5)'] * 2) * 0.2) +
    (np.log1p(combined_df['Seniority (Years)']) * 0.1)
)

final_rank = combined_df.sort_values(by="Capability_Index", ascending=False)

# Display Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Required Optimal Staff", f"{int(opt_staff)} FTEs")
m2.metric("System Workload", f"{weighted_load}")
m3.metric("Top Talent Recommendation", final_rank.iloc[0]["Teacher Name"])

# Visualization
fig = px.bar(final_rank, x="Teacher Name", y="Capability_Index", 
             color="Capability_Index", title="Staff Capability Optimization Map")
st.plotly_chart(fig, use_container_width=True)

st.success(f"**Final Decision:** Deploy {int(opt_staff)} teachers. Priority for high-impact classes: **{final_rank.iloc[0]['Teacher Name']}**.")
