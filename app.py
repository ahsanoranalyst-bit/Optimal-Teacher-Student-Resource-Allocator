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
        sn_weight = st.slider("SN Workload Multiplier", 1.0, 5.0, 2.0, 
                              help="Weight of one SN student vs one General student. Default is 2.0x.")

    # Logic A: Calculate Weighted System Workload
    total_gen = input_grades["General Students"].sum()
    total_sn = input_grades["Special Needs (SN)"].sum()
    weighted_load = total_gen + (total_sn * sn_weight)
    
    st.info(f"**Total Weighted Workload Units:** {weighted_load} (Reflecting {total_sn} SN students at {sn_weight}x load)")

st.write("---")

# =========================================================
# SECTION B: TEACHER PROFILE (INTERNAL DATA)
# =========================================================
st.header("🧑‍🏫 Section B: Teacher Profile & Metrics")
with st.container():
    b_data = pd.DataFrame({
        "Teacher Name": ["Aris", "Bo", "Cy", "Di", "El"],
        "Qualification": ["PhD", "Masters", "Masters", "Bachelors", "Masters"],
        "Seniority (Years)": [15, 8, 5, 2, 10],
        "Performance Metric": [9.6, 8.2, 7.5, 9.3, 8.7]
    })
    # Allow users to add/edit staff list
    edited_b_data = st.data_editor(b_data, use_container_width=True, num_rows="dynamic")

st.write("---")

# =========================================================
# SECTION C: EFFICIENCY (CONSTRAINTS)
# =========================================================
st.header("⚙️ Section C: Efficiency & Capacity")
with st.container():
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        target_ratio = st.number_input("Target Student-to-Teacher Ratio", 5, 50, 25)
    with col_c2:
        admin_hours = st.slider("Weekly Administrative Burden (Hours)", 0, 40, 6)

    # Logic C: Adjust capacity based on admin "leakage"
    # Assuming a 40-hour work week
    efficiency = (40 - admin_hours) / 40
    opt_staff = np.ceil((weighted_load / target_ratio) / efficiency)
    actual_staff_count = len(edited_b_data)

st.write("---")

# =========================================================
# SECTION D: FEEDBACK (EXTERNAL QUALITY)
# =========================================================
st.header("💬 Section D: Feedback & Satisfaction Scores")
with st.container():
    # Sync with edited names from Section B
    d_data = pd.DataFrame({
        "Teacher Name": edited_b_data["Teacher Name"],
        "Student Satisfaction %": [98, 85, 80, 95, 88][:len(edited_b_data)] if len(edited_b_data) <= 5 else [85]*len(edited_b_data),
        "Peer Review (1-5)": [4.9, 4.1, 3.5, 4.7, 4.2][:len(edited_b_data)] if len(edited_b_data) <= 5 else [4.0]*len(edited_b_data)
    })
    edited_d_data = st.data_editor(d_data, use_container_width=True)

st.write("---")

# =========================================================
# FINAL OPTIMIZATION ENGINE
# =========================================================
st.header("🚀 Strategic Staffing Optimization")

# Merge B and D for Capability Index
combined_df = pd.merge(edited_b_data, edited_d_data, on="Teacher Name")

# Optimization Logic: Weighted Capability Index
# Normalizing Peer Review and Satisfaction to a 10-point scale
combined_df['Capability_Index'] = (
    (combined_df['Performance Metric'] * 0.4) +
    ((combined_df['Student Satisfaction %'] / 10) * 0.3) +
    ((combined_df['Peer Review (1-5)'] * 2) * 0.2) +
    (np.log1p(combined_df['Seniority (Years)']) * 0.1)
)

final_rank = combined_df.sort_values(by="Capability_Index", ascending=False)

# Results Display - Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Optimal Staff Required", f"{int(opt_staff)} Teachers")
m2.metric("Current Staff Count", f"{actual_staff_count}")
gap = int(opt_staff - actual_staff_count)
m3.metric("Staffing Gap", f"{gap}", delta=-gap, delta_color="inverse")
m4.metric("System Efficiency", f"{efficiency*100:.1f}%")

# Optimization Visualization
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.subheader("Knowledge-Capability Mapping")
    fig_bar = px.bar(final_rank, x="Teacher Name", y="Capability_Index", 
                 color="Capability_Index", color_continuous_scale="Viridis")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_v2:
    st.subheader("Talent Dimensionality")
    # Radar Chart for Top Performer
    top_t = final_rank.iloc[0]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
          r=[top_t['Performance Metric'], top_t['Student Satisfaction %']/10, top_t['Peer Review (1-5)']*2, np.log1p(top_t['Seniority (Years)'])*2],
          theta=['Performance','Satisfaction','Peer Review', 'Seniority (Log)'],
          fill='toself',
          name=top_t['Teacher Name']
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])))
    st.plotly_chart(fig_radar, use_container_width=True)

# Final Guidance
if gap > 0:
    st.error(f"**Action Required:** You are understaffed by **{gap}** units. Consider hiring or reducing admin burden to {admin_hours - 5}h to recover capacity.")
else:
    st.success(f"**Optimization Summary:** Staffing is sufficient. Priority for high-load clusters: **{final_rank.iloc[0]['Teacher Name']}**.")

# Export Option
st.download_button("📩 Download Optimization Report", 
                   final_rank.to_csv(index=False), 
                   "staff_optimization.csv", 
                   "text/csv")
