import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuration
st.set_page_config(page_title="Teacher-Student Resource Allocator", layout="wide")

st.title("⚖️ Teacher-Student Resource Allocator")
st.markdown("Optimize staff distribution based on student needs, teacher seniority, and performance metrics.")

# --- SIDEBAR: PARAMETERS ---
with st.sidebar:
    st.header("Section A: Student Load")
    total_students = st.number_input("Total Student Population", 100, 5000, 500)
    special_needs_pct = st.slider("Special Needs Students (%)", 0, 50, 10)
    
    st.header("Section C: Efficiency Targets")
    target_ratio = st.slider("Target Student-Teacher Ratio", 10, 40, 25)
    admin_hours = st.number_input("Weekly Admin Hours per Teacher", 0, 20, 5)

# --- APP LAYOUT ---
tab1, tab2 = st.tabs(["📊 Allocation Engine", "📋 Teacher Profiles & Feedback"])

with tab1:
    st.header("Resource Allocation Logic")
    
    # Calculation Logic
    # Basic math: total students / target ratio
    required_teachers = int(np.ceil(total_students / target_ratio))
    
    # Weighted adjustment: Special needs students are treated as 2x load
    # adjusted_load = (General Students) + (Special Needs Students * 2)
    sn_count = total_students * (special_needs_pct / 100)
    gen_count = total_students - sn_count
    adjusted_load = gen_count + (sn_count * 2)
    
    optimized_staff_count = int(np.ceil(adjusted_load / target_ratio))

    c1, c2, c3 = st.columns(3)
    c1.metric("Standard Staff Needed", required_teachers)
    c2.metric("Optimized Staff (SN Adjusted)", optimized_staff_count)
    c3.metric("Additional Hiring Need", optimized_staff_count - required_teachers)

    st.info(f"**Efficiency Note:** Based on {admin_hours} admin hours/week, effective teaching time is {40 - admin_hours} hours per staff member.")

    # Visualization
    allocation_df = pd.DataFrame({
        "Category": ["General Education", "Special Education Support"],
        "Student Count": [gen_count, sn_count]
    })
    st.bar_chart(allocation_df.set_index("Category"))

with tab2:
    st.header("Section B & D: Teacher Merit & Feedback")
    
    # Mock Data
    teacher_data = pd.DataFrame({
        "Teacher Name": ["Mx. Alpha", "Mx. Beta", "Mx. Gamma", "Mx. Delta"],
        "Seniority (Years)": [12, 4, 8, 15],
        "Performance Score (1-10)": [9.2, 7.5, 8.8, 9.5],
        "Student Satisfaction (%)": [95, 82, 89, 91],
        "Peer Review Score": [4.8, 3.5, 4.2, 4.9]
    })
    
    st.subheader("Staff Performance Matrix")
    st.dataframe(teacher_data, use_container_width=True)
    
    # Recommendation Logic
    st.subheader("Smart Assignment Recommendation")
    high_performers = teacher_data[teacher_data["Performance Score (1-10)"] > 9]
    
    if not high_performers.empty:
        names = ", ".join(high_performers['Teacher Name'])
        st.success(f"**Recommended for High-Load/Special Needs:** {names}")
    else:
        st.warning("No teachers currently meet the high-performance threshold for specialized assignment.")
