import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import numpy as np
import os
import time

# --- 1. PAGE SETUP ---
st.set_page_config(
    page_title="System Intelligence | Core Nexus",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ADVANCED ANIMATED CSS ---
st.markdown("""
    <style>
    /* Dark Sci-Fi Theme */
    .stApp {
        background: #020c1b;
        color: #ccd6f6;
    }
    
    /* Animation for Glowing Text */
    @keyframes glow {
        0% { text-shadow: 0 0 5px #64ffda; }
        50% { text-shadow: 0 0 20px #64ffda, 0 0 30px #ffd700; }
        100% { text-shadow: 0 0 5px #64ffda; }
    }

    /* Centering Top Titles & Removing Boxes */
    .top-header {
        text-align: center;
        padding: 20px;
        animation: glow 3s infinite;
    }

    .main-title {
        color: #64ffda;
        font-size: 35px;
        font-weight: bold;
        letter-spacing: 4px;
        margin-bottom: 0px;
    }

    .sub-title {
        color: #ffd700;
        font-size: 22px;
        letter-spacing: 2px;
        margin-top: -10px;
    }

    /* Clean Panels without extra boxes */
    .glass-panel {
        background: rgba(17, 34, 64, 0.6);
        border: 1px solid rgba(100, 255, 218, 0.3);
        border-radius: 15px;
        padding: 20px;
        transition: 0.5s;
    }
    .glass-panel:hover {
        border-color: #64ffda;
        box-shadow: 0 0 15px rgba(100, 255, 218, 0.4);
    }

    /* Large Centered Logo Styling */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
    }

    /* Metrics with Pulse */
    .metric-card {
        background: rgba(10, 25, 47, 0.8);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border-bottom: 3px solid #64ffda;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. TOP SECTION (NOW FULLY CENTERED) ---
st.markdown('<div class="top-header">', unsafe_allow_html=True)
st.markdown('<p class="main-title">PARTICIPATING COUNTRIES GLOBAL HUB</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">PK • CN • US • DE • GB • BR • AU</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. MAIN LAYOUT ---
col_left, col_center, col_right = st.columns([1, 2, 1], gap="medium")

# --- LEFT: NETWORK INTELLIGENCE ---
with col_left:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#64ffda; text-align:center;'>NETWORK INTEL</h3>", unsafe_allow_html=True)
    
    # Animated-like list
    nations = ["🇵🇰 PAKISTAN", "🇨🇳 CHINA", "🇺🇸 USA", "🇩🇪 GERMANY"]
    for n in nations:
        st.info(f"CONNECTED: {n}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="metric-card"><h2 style="color:white; margin:0;">18ms</h2><small>PING RATE</small></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- CENTER: LARGE LOGO & EARTH ---
with col_center:
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    
    # Large Logo Logic
    if os.path.exists('logo_nexus.png'):
        st.image('logo_nexus.png', width=500) # Increased size significantly
    else:
        st.markdown('<div style="font-size:120px; color:#64ffda; border:5px solid #64ffda; display:inline-block; padding:30px 60px; border-radius:20px; box-shadow: 0 0 30px #64ffda;">Si</div>', unsafe_allow_html=True)
    
    st.markdown("<h2 style='color:#ffd700; letter-spacing:3px;'>SYSTEM INTELLIGENCE CORE NEXUS</h2>", unsafe_allow_html=True)
    
    # Animated Map
    fig = go.Figure(go.Scattergeo(
        lat=[30, 35, 37, 51], lon=[69, 104, -95, 10],
        mode='lines+markers',
        line=dict(width=2, color='#ffd700'),
        marker=dict(size=8, color='#64ffda', symbol='diamond')
    ))
    fig.update_layout(
        geo=dict(projection_type='orthographic', showland=True, landcolor='#0a192f', oceancolor='#020c1b', showocean=True, bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0, r=0, t=0, b=0), height=450, paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT: LIVE DASHBOARD ---
with col_right:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#64ffda; text-align:center;'>CORE DASHBOARD</h3>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:#64ffda;'>SYSTEM STATUS: <span style='color:#ffd700;'>ACTIVE</span></p>", unsafe_allow_html=True)
    st.progress(91) # Visual progress bar
    
    c1, c2 = st.columns(2)
    with c1: st.markdown('<div class="metric-card"><h3 style="color:white; margin:0;">87%</h3><small>PROFIT</small></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="metric-card"><h3 style="color:white; margin:0;">91%</h3><small>EFFICIENCY</small></div>', unsafe_allow_html=True)
    
    st.markdown("<br><p style='color:#64ffda;'>LIVE TRAFFIC LOGS</p>", unsafe_allow_html=True)
    st.caption("• [SYNC] Hub-PK Active")
    st.caption("• [FLOW] Energy: CN -> PK")
    
    if st.button("TRIGGER DIAGNOSTIC"):
        with st.spinner('Scanning Global Nodes...'):
            time.sleep(2)
            st.success('Global Systems Optimal!')
    st.markdown('</div>', unsafe_allow_html=True)
