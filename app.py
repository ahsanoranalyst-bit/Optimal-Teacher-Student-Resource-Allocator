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
# SIDEBAR: CONTROLS (As seen in your screenshot)
# =========================================================
with st.sidebar:
    st.header("Section A: Student Load")
    total_students = st.number_input("Total Student Population", value=800, step=10)
    sn_percent = st.slider("Special Needs Students (%)", 0, 100, 16)
    sn_weight = st.slider("SN Workload Multiplier", 1.0, 3.0, 2.0)

    st.header("Section C: Efficiency")
    target_ratio = st.slider("Target Ratio (Students per Teacher)", 5, 50, 22)
    admin_hours = st.number_input("Weekly Admin Hours", value=4, step=1)

# =========================================================
# MAIN LOGIC: CALCULATIONS
# =========================================================
# 1. Load Calculations
sn_count = total_students * (sn_percent / 100)
gen_count = total_students - sn_count
weighted_load = gen_count + (sn_count * sn_weight)

# 2. Efficiency Calculations (Assuming 40hr week)
efficiency = (40 - admin_hours) / 40
opt_staff_req = np.ceil((weighted_load / target_ratio) / efficiency)

# =========================================================
# MAIN PAGE: SECTION B & D (MISSING COMPONENTS)
# =========================================================

# --- TOP METRICS BAR ---
m1, m2, m3 = st.columns(3)
m1.metric("Raw Student Count", int(total_students))
m2.metric("Weighted Load", f"{weighted_load:.1f}")
m3.metric("Required Staff", int(opt_staff_req))

st.write("---")

# --- SECTION B: TEACHER PROFILE ---
st.header("🧑‍🏫 Section B: Teacher Profile (Internal)")
st.info("Define staff seniority, qualifications, and internal performance metrics.")

b_data = pd.DataFrame({
    "Teacher Name": ["Aris", "Bo", "Cy", "Di", "El"],
    "Qualification": ["PhD", "Masters", "Masters", "Bachelors", "Masters"],
    "Seniority (Years)": [15, 8, 5, 2, 10],
    "Performance Metric": [9.6, 8.2, 7.5, 9.3, 8.7]
})

edited_b = st.data_editor(b_data, use_container_width=True, num_rows="dynamic", key="sec_b")

# --- SECTION D: FEEDBACK ---
st.header("💬 Section D: Feedback (External)")
st.info("Input student satisfaction and peer review data for the staff listed above.")

# Create a feedback template based on names in Section B
d_template = pd.DataFrame({
    "Teacher Name": edited_b["Teacher Name"],
    "Student Satisfaction %": [90] * len(edited_b),
    "Peer Review (1-5)": [4.0] * len(edited_b)
})

edited_d = st.data_editor(d_template, use_container_width=True, key="sec_d")

st.write("---")

# =========================================================
# FINAL OPTIMIZATION ENGINE
# =========================================================
st.header("🚀 Optimization Results")

if not edited_b.empty and not edited_d.empty:
    # Merge B and D
    combined = pd.merge(edited_b, edited_d, on="Teacher Name")

    # Weighted Scoring Logic
    combined['Capability_Score'] = (
        (combined['Performance Metric'] * 0.4) +
        ((combined['Student Satisfaction %'] / 10) * 0.3) +
        ((combined['Peer Review (1-5)'] * 2) * 0.2) +
        (np.log1p(combined['Seniority (Years)']) * 0.1)
    )

    final_rank = combined.sort_values(by="Capability_Score", ascending=False)

    # Visualization
    fig = px.bar(final_rank, x="Teacher Name", y="Capability_Score", 
                 color="Capability_Score", title="Teacher Capability Index",
                 color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

    # Success Message
    top_t = final_rank.iloc[0]["Teacher Name"]
    st.success(f"**Optimal Allocation:** Based on the weighted load of **{weighted_load}**, you need **{int(opt_staff_req)}** teachers. **{top_t}** is ranked as your highest-capability resource.")
else:
    st.warning("Please ensure teacher data is entered in Section B.")
