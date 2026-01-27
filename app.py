import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# CORE ENGINE: OPTIMIZATION METHODS
# ==========================================
class StaffingOptimizer:
    @staticmethod
    def process_section_a(grade_df, sn_multiplier):
        """Logic: Calculate Weighted Student Load"""
        grade_df['Weighted_Load'] = grade_df['General_Count'] + (grade_df['SN_Count'] * sn_multiplier)
        return grade_df, grade_df['Weighted_Load'].sum()

    @staticmethod
    def process_section_b_d(teacher_df, weights):
        """Logic: Multi-Criteria Decision Analysis for Teacher Quality"""
        # Section B: Profile Logic
        perf_score = teacher_df['Performance_Score'] * weights['performance']
        seniority_score = np.log1p(teacher_df['Seniority_Years']) * weights['seniority']
        
        # Section D: Feedback Logic
        sat_score = (teacher_df['Student_Sat_Pct'] / 10) * weights['satisfaction']
        peer_score = teacher_df['Peer_Review_Score'] * weights['peer_review']
        
        teacher_df['Composite_Capability'] = perf_score + seniority_score + sat_score + peer_score
        return teacher_df.sort_values(by='Composite_Capability', ascending=False)

    @staticmethod
    def process_section_c(total_load, target_ratio, admin_hours):
        """Logic: Efficiency & Capacity Constraints"""
        available_hours_pct = (40 - admin_hours) / 40
        raw_staff_needed = total_load / target_ratio
        optimized_staff = raw_staff_needed / available_hours_pct
        return np.ceil(optimized_staff), available_hours_pct

# ==========================================
# STREAMLIT UI - SEPARATED SECTIONS
# ==========================================
st.set_page_config(page_title="OR Resource Allocator", layout="wide")
st.title("⚖️ Optimal Teacher-Student Resource Allocator")

# --- SECTION A: STUDENT LOAD ---
st.header("📍 Section A: Student Load Profile")
with st.container(border=True):
    col_a1, col_a2 = st.columns([2, 1])
    with col_a1:
        grade_data = pd.DataFrame({
            "Grade_Level": ["Primary", "Middle", "High School"],
            "General_Count": [300, 250, 200],
            "SN_Count": [30, 20, 10]
        })
        input_grades = st.data_editor(grade_data, use_container_width=True)
    with col_a2:
        sn_weight = st.slider("SN Workload Multiplier", 1.0, 3.0, 2.0)
    
    _, total_load = StaffingOptimizer.process_section_a(input_grades, sn_weight)
    st.info(f"**Total Calculated Workload Units:** {total_load}")

# --- SECTION B & D: TEACHER CAPABILITY ---
st.header("🧑‍🏫 Section B & D: Teacher Merit & Feedback")
with st.container(border=True):
    # Mock Data combining Profile (B) and Feedback (D)
    teacher_data = pd.DataFrame({
        "Teacher_Name": ["Aris", "Bo", "Cy", "Di", "El"],
        "Qualification": ["PhD", "MA", "MA", "BA", "MA"],
        "Seniority_Years": [15, 8, 5, 2, 10],       # Section B
        "Performance_Score": [9.5, 8.0, 7.5, 9.0, 8.2], # Section B
        "Student_Sat_Pct": [98, 85, 80, 92, 88],    # Section D
        "Peer_Review_Score": [4.9, 4.2, 3.5, 4.5, 4.0] # Section D
    })
    
    st.subheader("Optimization Weights (Analyst Control)")
    cw1, cw2, cw3, cw4 = st.columns(4)
    w_perf = cw1.number_input("B: Performance Weight", 0.0, 1.0, 0.4)
    w_sen = cw2.number_input("B: Seniority Weight", 0.0, 1.0, 0.2)
    w_sat = cw3.number_input("D: Satisfaction Weight", 0.0, 1.0, 0.2)
    w_peer = cw4.number_input("D: Peer Review Weight", 0.0, 1.0, 0.2)
    
    weights = {"performance": w_perf, "seniority": w_sen, "satisfaction": w_sat, "peer_review": w_peer}
    ranked_teachers = StaffingOptimizer.process_section_b_d(teacher_data, weights)
    st.dataframe(ranked_teachers, use_container_width=True)

# --- SECTION C: EFFICIENCY ---
st.header("⚙️ Section C: Efficiency Constraints")
with st.container(border=True):
    ec1, ec2 = st.columns(2)
    with ec1:
        target_ratio = st.number_input("Target Student-to-Teacher Ratio", 10, 50, 25)
    with ec2:
        admin_hours = st.slider("Weekly Administrative Hours per Staff", 0, 20, 5)

# --- FINAL OPTIMIZATION OUTPUT ---
st.divider()
st.header("🚀 Final Optimization Results")
opt_staff, efficiency = StaffingOptimizer.process_section_c(total_load, target_ratio, admin_hours)

res1, res2, res3 = st.columns(3)
res1.metric("Optimal Staff Needed", f"{int(opt_staff)} FTEs")
res2.metric("System Efficiency", f"{efficiency*100:.1f}%")
res3.metric("Top Talent Recommendation", ranked_teachers.iloc[0]['Teacher_Name'])



# Visualization of Resource Mapping
st.subheader("Teacher Capability vs. Seniority Map")
fig = px.scatter(ranked_teachers, x="Seniority_Years", y="Composite_Capability", 
                 size="Performance_Score", color="Teacher_Name",
                 title="Strategic Staff Positioning (Sections B & D)")
st.plotly_chart(fig, use_container_width=True)
