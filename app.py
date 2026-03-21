import streamlit as st
import pandas as pd
import time
import random
import plotly.graph_objects as go
from datetime import datetime

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="System Intelligence | Ahsan Khan",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Advanced UI Styling (Cyan & Gold) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Courier+Prime&display=swap');

    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top right, #0a192f 0%, #010101 100%);
        color: #ccd6f6;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #020c1b !important;
        border-right: 1px solid #00FFFF;
    }

    .glow-text {
        color: #FFD700 !important;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.8);
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        text-align: center;
    }

    .logic-card {
        background: rgba(17, 34, 64, 0.6);
        border: 1px solid rgba(0, 255, 255, 0.4);
        padding: 25px;
        border-radius: 15px;
        transition: 0.4s;
        box-shadow: inset 0 0 15px rgba(0, 255, 255, 0.1);
    }

    .logic-card:hover {
        border-color: #FFD700;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.2);
        transform: translateY(-5px);
    }

    /* System Log Styling */
    .system-log {
        font-family: 'Courier Prime', monospace;
        font-size: 0.8rem;
        color: #00FFFF;
        background: black;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Sidebar (Live System Monitor) ---
with st.sidebar:
    st.markdown("<h3 style='color:#FFD700; text-align:center;'>SYSTEM MONITOR</h3>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("🟢 **Status:** Operational")
    st.write(f"📅 **Date:** {datetime.now().strftime('%d %b, %Y')}")
    st.write("🛰️ **Neural Sync:** Active")
    
    st.markdown("<p style='font-size: 0.7rem; color:#888;'>LIVE COMMAND LOG</p>", unsafe_allow_html=True)
    logs = [
        "> Syncing OR-Nodes...",
        "> Mapping Constraints...",
        "> Loading 2100+ Profiles...",
        "> Success: Matrix Built"
    ]
    for log in logs:
        st.markdown(f"<div class='system-log'>{log}</div>", unsafe_allow_html=True)
        st.write("")

# --- 4. Hero Header ---
st.markdown("<h1 class='glow-text' style='font-size: 4rem; margin-bottom:0;'>SYSTEM INTELLIGENCE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00FFFF; letter-spacing: 6px; font-weight:bold;'>THE STRATEGIC BUILDING ENGINE</p>", unsafe_allow_html=True)
st.write("---")

# --- 5. The Decision Pipeline (Visual Steps) ---
st.subheader("📡 Optimization Pipeline")
p_col1, p_col2, p_col3, p_col4, p_col5 = st.columns(5)
pipeline = ["Raw Data", "Constraints", "OR-Logic", "Architecture", "Solution"]

for i, step in enumerate(pipeline):
    with [p_col1, p_col2, p_col3, p_col4, p_col5][i]:
        st.markdown(f"""
        <div style="text-align: center; border: 1px solid rgba(0,255,255,0.2); padding: 10px; border-radius: 10px;">
            <small style="color:#FFD700;">PHASE 0{i+1}</small><br>
            <b style="color:white;">{step}</b>
        </div>
        """, unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# --- 6. Core Narrative & ROI ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 💠 The Mathematical Builder")
    st.markdown("""
    <div class="logic-card">
    <b>I am built on the science of Operations Research.</b><br><br>
    While others offer opinions, I offer <b>certainty</b>. I analyze billions of possible 
    combinations in institutional workflows to provide the single most efficient path. 
    Whether it's 100 projects or 2,100, my logic scales with your vision.
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("### ⏱️ Impact Calculator")
    m_hours = st.number_input("Est. Manual Work (Hrs)", value=200)
    saved = m_hours * 0.98
    st.markdown(f"""
    <div style="text-align: center; background: rgba(0, 255, 255, 0.1); padding: 15px; border-radius: 15px; border: 1px solid #00FFFF;">
        <span style="font-size: 0.9rem; color: #FFD700;">SYSTEM SAVINGS</span><br>
        <span style="font-size: 2.2rem; font-weight: bold; color: white;">{int(saved)} Hrs</span><br>
        <small style="color: #00FFFF;">Optimization Gain: 98%</small>
    </div>
    """, unsafe_allow_html=True)

# --- 7. Deployment Modules ---
st.write("---")
st.subheader("🛠️ Active Decision Modules")

tab1, tab2, tab3 = st.tabs(["[Module 01: Timetable]", "[Module 02: Resource]", "[Module 03: Risk]"])

with tab1:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.write("#### Neural Timetable Solver")
        if st.button("EXECUTE NEURAL SOLVE"):
            with st.status("Building Global Matrix...", expanded=True) as status:
                st.write("Assigning 2100+ Parameters...")
                time.sleep(1)
                st.write("Eliminating Overlaps...")
                time.sleep(1)
                status.update(label="STRATEGY READY", state="complete", expanded=False)
            st.success("Mathematical Balance Achieved.")
            st.dataframe(pd.DataFrame({
                'Metric': ['Efficiency', 'Conflicts', 'Satisfaction'],
                'Score': ['99.2%', '0', 'High']
            }), use_container_width=True)
    with c2:
        # Plotly Gauge Chart for Logic Health
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 99.2,
            title = {'text': "Solution Precision", 'font': {'color': '#FFD700', 'size': 18}},
            gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#00FFFF"}}
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#00FFFF", height=250, margin=dict(l=20,r=20,t=40,b=20))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.info("Resource Optimizer: Analyzing 2,100 solution paths for maximum utility.")
    st.progress(85)

with tab3:
    st.warning("Risk Predictor: Identify institutional bottlenecks before they occur.")
    st.write("`Current Neural Accuracy: 94.8%`")

# --- 8. Professional Footer ---
st.write("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; border-top: 1px solid rgba(255, 215, 0, 0.3); padding-top: 25px;">
    <p style="font-family: 'Courier Prime'; font-size: 0.85rem; color: #ccd6f6;">
        <b>SYSTEM INTELLIGENCE GROUP</b> | ARCHITECT: AHSAN KHAN | {datetime.now().year} <br>
        <span style="color: #00FFFF;">Powered by Operations Research & Strategic Logic</span>
    </p>
</div>
""", unsafe_allow_html=True)
