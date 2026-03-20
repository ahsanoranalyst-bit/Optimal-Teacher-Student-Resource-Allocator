import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import numpy as np
import time
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="System Intelligence | Global Command Center",
    layout="wide",
    page_icon="💠",
    initial_sidebar_state="collapsed"
)

# --- 2. PREMIUM CSS STYLING (Cyan & Gold) ---
st.markdown(f"""
    <style>
    .stApp {{
        background: radial-gradient(circle at center, #020c1b, #0a192f);
        color: #ccd6f6;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}
    
    .block-container {{
        padding-top: 1.5rem;
        max-width: 95%;
    }}

    /* Panel Styling */
    .main-panel {{
        background: rgba(17, 34, 64, 0.8);
        border: 2px solid #64ffda;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(100, 255, 218, 0.2);
    }}
    
    .gold-nexus-panel {{
        border: 2px solid #ffd700;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.2);
    }}

    /* HEADER BOXES (Fixed the empty box issue) */
    .header-box {{
        background: rgba(100, 255, 218, 0.1);
        border: 1px solid #64ffda;
        border-radius: 10px;
        color: #64ffda;
        text-align: center;
        padding: 12px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 25px;
    }}
    
    .gold-header-box {{
        background: rgba(255, 215, 0, 0.1);
        border: 1px solid #ffd700;
        color: #ffd700;
    }}

    /* List Items */
    .data-card {{
        background: rgba(100, 255, 218, 0.05);
        border-left: 3px solid #64ffda;
        padding: 12px;
        margin-bottom: 10px;
        border-radius: 5px;
        display: flex;
        justify-content: space-between;
    }}

    /* Metrics Styling */
    .stat-box {{
        text-align: center;
        padding: 15px;
        background: rgba(0,0,0,0.2);
        border-radius: 10px;
        border: 1px solid rgba(100, 255, 218, 0.3);
    }}
    
    .stat-value {{ font-size: 24px; font-weight: bold; color: #ffffff; }}
    .stat-label {{ font-size: 12px; color: #64ffda; text-transform: uppercase; }}

    /* Button Visibility Fix */
    .stButton>button {{
        width: 100%;
        background: transparent;
        color: #64ffda !important;
        border: 1px solid #64ffda !important;
        font-weight: bold;
        padding: 10px;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background: #64ffda !important;
        color: #020c1b !important;
        box-shadow: 0 0 15px #64ffda;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIC ---
def get_map():
    fig = go.Figure()
    # Coordinates for connections
    locations = {'PK': [30.3753, 69.3451], 'CN': [35.8617, 104.1954], 'US': [37.0902, -95.7129], 'DE': [51.1657, 10.4515]}
    pk = locations['PK']
    
    for code, coords in locations.items():
        if code != 'PK':
            fig.add_trace(go.Scattergeo(
                lat = [pk[0], coords[0]], lon = [pk[1], coords[1]],
                mode = 'lines+markers',
                line = dict(width = 2, color = '#ffd700'),
                marker = dict(size = 6, color = '#64ffda')
            ))

    fig.update_layout(
        geo = dict(projection_type = 'orthographic', showland = True, landcolor = '#020c1b', bgcolor = 'rgba(0,0,0,0)', oceancolor='#0a192f', showocean=True),
        margin = dict(l=0, r=0, t=0, b=0), height=400, paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# --- 4. TOP BANNER (Participating Countries) ---
st.markdown('<div style="text-align:center; padding:10px; border-bottom:1px solid #64ffda; margin-bottom:30px;">', unsafe_allow_html=True)
st.markdown('<h3 style="color:#64ffda; letter-spacing:3px;">PARTICIPATING COUNTRIES GLOBAL HUB</h3>', unsafe_allow_html=True)
st.markdown('<p style="color:#ffd700; font-size:20px;">PK • CN • US • DE • GB • BR • AU</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. MAIN LAYOUT ---
col1, col2, col3 = st.columns([1, 2, 1], gap="large")

# --- LEFT COLUMN: NETWORK INFO ---
with col1:
    st.markdown('<div class="main-panel">', unsafe_allow_html=True)
    st.markdown('<div class="header-box">GLOBAL NETWORK INTELLIGENCE</div>', unsafe_allow_html=True)
    
    st.markdown("<p style='color:#64ffda; font-weight:bold;'>CONNECTED NATIONS</p>", unsafe_allow_html=True)
    nations = [("🇵🇰 PAKISTAN", "PK"), ("🇨🇳 CHINA", "CN"), ("🇺🇸 USA", "US"), ("🇩🇪 GERMANY", "DE")]
    for name, code in nations:
        st.markdown(f'<div class="data-card"><span>{name}</span><span style="color:#ffd700;">{code}</span></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="stat-box"><div class="stat-value">18ms</div><div class="stat-label">Response Time</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-box" style="margin-top:10px;"><div class="stat-value">99.9%</div><div class="stat-label">Uptime</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- CENTER COLUMN: NEXUS & MAP ---
with col2:
    st.markdown('<div class="main-panel gold-nexus-panel" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown('<div class="header-box gold-header-box">GLOBAL NEXUS FLOW VISUALIZATION</div>', unsafe_allow_html=True)
    
    # Nexus Logo Logic
    if os.path.exists('logo_nexus.png'):
        st.image('logo_nexus.png', width=350)
    else:
        st.markdown('<div style="font-size:80px; font-weight:bold; color:#64ffda; text-shadow: 0 0 20px #64ffda; border:4px solid #64ffda; display:inline-block; padding:20px 40px; border-radius:15px; margin-bottom:15px;">Si</div>', unsafe_allow_html=True)
    
    st.markdown('<h4 style="color:#ffd700;">SYSTEM INTELLIGENCE CORE</h4>', unsafe_allow_html=True)
    
    # 3D Map
    st.plotly_chart(get_map(), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT COLUMN: DASHBOARD METRICS ---
with col3:
    st.markdown('<div class="main-panel">', unsafe_allow_html=True)
    st.markdown('<div class="header-box">NETWORK DASHBOARD</div>', unsafe_allow_html=True)
    
    st.markdown("<p style='color:#64ffda; font-weight:bold;'>ADVANTAGE METRICS</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown('<div class="stat-box"><div class="stat-value">87%</div><div class="stat-label">Profit</div></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="stat-box"><div class="stat-value">91%</div><div class="stat-label">Efficiency</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64ffda; font-weight:bold;'>SYSTEM HEALTH: <span style='color:#ffd700;'>OPTIMAL</span></p>", unsafe_allow_html=True)
    st.progress(0.95)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64ffda; font-weight:bold;'>RECENT LOGS</p>", unsafe_allow_html=True)
    st.markdown('<div class="data-card" style="font-size:11px;"><span>[20:54] RETAIL: AU -> UAE</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="data-card" style="font-size:11px;"><span>[21:10] ENERGY: PK -> CN</span></div>', unsafe_allow_html=True)
    
    st.button("RUN FULL DIAGNOSTIC")
    st.markdown('</div>', unsafe_allow_html=True)
