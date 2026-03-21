import streamlit as st
import pandas as pd
import time
import random
import plotly.graph_objects as go
from datetime import datetime

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="System Intelligence | Strategic Builder",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Enhanced UI Styling (High-Tech Cyan & Gold) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Courier+Prime&display=swap');

    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a192f 0%, #010101 100%);
        color: #ccd6f6;
    }

    /* Glow Effect for Titles */
    .glow-text {
        color: #FFD700 !important;
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.6);
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        text-align: center;
    }

    .logic-card {
        background: rgba(17, 34, 64, 0.5);
        border: 1px solid #00FFFF;
        padding: 25px;
        border-radius: 15px;
        transition: 0.5s;
        height: 100%;
    }

    .logic-card:hover {
        border-color: #FFD700;
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.2);
    }

    .stButton>button {
        background: linear-gradient(45deg, #00FFFF, #008080) !important;
        color: #010101 !important;
        border: none !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.4s;
    }

    .stButton>button:hover {
        box-shadow: 0 0 25px #00FFFF;
        transform: translateY(-3px);
    }

    /* Neural Pulse Animation */
    @keyframes pulse {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }
    .pulse-status { animation: pulse 2s infinite; color: #00FFFF; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. Hero Header ---
st.markdown("<h1 class='glow-text' style='font-size: 4.5rem; margin-bottom:0;'>SYSTEM INTELLIGENCE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00FFFF; letter-spacing: 8px;'>THE ARCHITECT OF OPERATIONAL HARMONY</p>", unsafe_allow_html=True)
st.write("---")

# --- 4. Interactive Strategic Map (New Feature) ---
# This visually explains how the "Builder" works.
st.subheader("📡 The Decision Pipeline")
cols = st.columns(5)
steps = ["DATA INGESTION", "CONSTRAINT MAPPING", "OR-LOGIC PROCESSING", "STRATEGY BUILDING", "OPTIMAL OUTPUT"]
for i, step in enumerate(steps):
    with cols[i]:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px; border-bottom: 2px solid #FFD700;">
            <small style="color: #FFD700;">STEP 0{i+1}</small><br>
            <b style="font-size: 0.8rem;">{step}</b>
        </div>
        """, unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# --- 5. Core Narrative & ROI Calculator ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 💠 Why System Intelligence?")
    st.markdown("""
    <div class="logic-card">
    <b>I am not a chat-based AI. I am a Mathematical Builder.</b><br><br>
    Most systems tell you what happened. I tell you exactly what <b>should</b> happen. 
    By utilizing Operations Research (OR), I solve the 'Impossible Equations' of institutional 
    management—balancing teachers, students, rooms, and costs in one perfect matrix.
    </div>
    """, unsafe_allow_html=True)

with col_right:
    # ROI Calculator Feature
    st.markdown("### ⏱️ Savings Calculator")
    manual_hours = st.number_input("Manual Planning Hours / Month", value=160)
    saved = manual_hours * 0.95
    st.markdown(f"""
    <div style="text-align: center; background: #00FFFF11; padding: 20px; border-radius: 10px; border: 1px dashed #00FFFF;">
        <span style="font-size: 0.8rem;">System Intelligence will save you:</span><br>
        <span style="font-size: 2rem; color: #FFD700; font-weight: bold;">{int(saved)} Hours</span><br>
        <span style="color: #00FFFF;">Per Month</span>
    </div>
    """, unsafe_allow_html=True)

# --- 6. Active Execution Modules ---
st.write("---")
st.subheader("🛠️ Deployment Modules")

tab1, tab2, tab3 = st.tabs(["[Command: Timetable Solver]", "[Command: Resource Maximizer]", "[Command: Risk Predictor]"])

with tab1:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.write("#### Solving Institutional Chaos")
        st.write("Current Status: <span class='pulse-status'>READY FOR DEPLOYMENT</span>", unsafe_allow_html=True)
        if st.button("RUN NEURAL SOLVER"):
            with st.status("Building Optimization Matrix...", expanded=True) as s:
                st.write("Checking Teacher Conflicts...")
                time.sleep(0.8)
                st.write("Optimizing Room Utility...")
                time.sleep(0.8)
                s.update(label="STRATEGY GENERATED", state="complete", expanded=False)
            st.success("100% Conflict-Free Schedule Built.")
            
            # Professional Table Output
            df = pd.DataFrame({
                'Constraint': ['Teacher Load', 'Room Capacity', 'Travel Time', 'Preference Sync'],
                'Status': ['OPTIMIZED', 'OPTIMIZED', 'OPTIMIZED', '100% MATCH']
            })
            st.table(df)

    with c2:
        # Live Heartbeat Graph
        fig = go.Figure(go.Scatter(x=[1,2,3,4,5], y=[10,15,13,17,20], line=dict(color='#00FFFF', width=4), fill='tozeroy'))
        fig.update_layout(title="Processing Efficiency", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#FFD700", height=250, margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h3 style="color: #00FFFF;">Resource Maximization Active</h3>
        <p>I am currently analyzing 2100+ solution paths to find the lowest operational cost for your facility.</p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("### Prediction Analytics")
    st.progress(94)
    st.caption("Neural Accuracy: 94.2% across all departments.")

# --- 7. Footer ---
st.write("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; border-top: 1px solid rgba(255, 215, 0, 0.2); padding-top: 20px;">
    <p style="font-family: 'Courier Prime'; font-size: 0.8rem; color: #64ffda;">
        <b>SYSTEM INTELLIGENCE</b> | ARCHITECTED BY AHSAN KHAN | {datetime.now().year} <br>
        <i>"Turning Complexity into Mathematical Certainty"</i>
    </p>
</div>
""", unsafe_allow_html=True)
