import streamlit as st
import plotly.graph_objects as go
import numpy as np
import os
import time

# --- 1. GLOBAL SYSTEM CONFIG ---
st.set_page_config(
    page_title="SYSTEM INTELLIGENCE | GLOBAL HUB",
    layout="wide",
    page_icon="💠",
    initial_sidebar_state="collapsed"
)

# --- 2. INTERNATIONAL STANDARD UI (CSS) ---
st.markdown("""
    <style>
    /* Professional Dark Space Theme */
    .stApp {
        background: radial-gradient(circle at center, #051622 0%, #020c1b 100%);
        color: #ccd6f6;
        font-family: 'Inter', sans-serif;
    }

    /* Moving Background Grid Overlay */
    .stApp::before {
        content: "";
        position: absolute;
        width: 100%;
        height: 100%;
        background-image: linear-gradient(rgba(100, 255, 218, 0.03) 1px, transparent 1px), 
                          linear-gradient(90deg, rgba(100, 255, 218, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        z-index: -1;
    }

    /* Unified Animated Header */
    .main-hub-header {
        text-align: center;
        padding: 40px 0;
        background: linear-gradient(90deg, transparent, rgba(100, 255, 218, 0.1), transparent);
        border-top: 1px solid rgba(100, 255, 218, 0.3);
        border-bottom: 1px solid rgba(100, 255, 218, 0.3);
        margin-bottom: 40px;
    }
    
    .hub-title {
        color: #64ffda;
        font-size: 42px;
        font-weight: 900;
        letter-spacing: 8px;
        text-transform: uppercase;
        margin: 0;
        text-shadow: 0 0 20px rgba(100, 255, 218, 0.5);
    }

    .hub-sub {
        color: #ffd700;
        font-size: 18px;
        letter-spacing: 5px;
        margin-top: 10px;
        opacity: 0.8;
    }

    /* High-Tech Panels */
    .panel-container {
        background: rgba(10, 25, 47, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(100, 255, 218, 0.2);
        border-radius: 20px;
        padding: 25px;
        height: 100%;
        transition: all 0.4s ease;
    }
    .panel-container:hover {
        border-color: #64ffda;
        box-shadow: 0 0 30px rgba(100, 255, 218, 0.15);
        transform: translateY(-5px);
    }

    /* Animated Status Indicator */
    .status-pulse {
        width: 10px;
        height: 10px;
        background: #64ffda;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        box-shadow: 0 0 10px #64ffda;
        animation: pulse-animation 2s infinite;
    }
    @keyframes pulse-animation {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(100, 255, 218, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(100, 255, 218, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(100, 255, 218, 0); }
    }

    /* Core Nexus Glow */
    .nexus-portal {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
        position: relative;
    }
    .nexus-portal::after {
        content: "";
        position: absolute;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(100, 255, 218, 0.15) 0%, transparent 70%);
        animation: rotate-glow 10s linear infinite;
    }
    @keyframes rotate-glow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    /* Large Si Brand Styling */
    .si-brand-text {
        font-size: 140px;
        font-weight: 900;
        color: #ffffff;
        text-shadow: 0 0 30px #64ffda, 0 0 60px #ffd700;
        margin: 0;
        line-height: 1;
        z-index: 2;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DYNAMIC LOGIC ---
def create_global_map():
    # Coords for international hubs
    lats = [30.3, 35.8, 37.0, 51.1, -14.2, -25.2, 23.4]
    lons = [69.3, 104.1, -95.7, 10.4, -51.9, 133.7, 53.8]
    
    fig = go.Figure()
    
    # Adding global data streams (moving lines effect)
    for i in range(len(lats)):
        fig.add_trace(go.Scattergeo(
            lat=[30.3, lats[i]], lon=[69.3, lons[i]],
            mode='lines',
            line=dict(width=1.5, color='rgba(100, 255, 218, 0.4)'),
            opacity=0.6
        ))
        
    fig.add_trace(go.Scattergeo(
        lat=lats, lon=lons,
        mode='markers',
        marker=dict(size=10, color='#ffd700', symbol='hexagon', line=dict(width=2, color='#64ffda')),
        name='Global Nodes'
    ))

    fig.update_layout(
        geo=dict(
            projection_type='orthographic',
            showland=True, landcolor='#0a192f',
            showocean=True, oceancolor='#020c1b',
            showcountries=True, countrycolor='#112240',
            bgcolor='rgba(0,0,0,0)',
            center=dict(lat=20, lon=70) # Focused on the Hub region
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=550,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# --- 4. TOP HUB SECTION ---
st.markdown("""
    <div class="main-hub-header">
        <h1 class="hub-title">Participating Countries Global Hub</h1>
        <p class="hub-sub">PK • CN • US • DE • GB • BR • AU</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. DASHBOARD GRID ---
col_left, col_center, col_right = st.columns([1, 2, 1], gap="large")

# -- Left Panel: Intelligence Network --
with col_left:
    st.markdown('<div class="panel-container">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#64ffda; margin-top:0;'>GLOBAL INTEL</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 0.5px solid rgba(100, 255, 218, 0.2);'>", unsafe_allow_html=True)
    
    stats = [
        ("ACTIVE NODES", "42 / 50", "100%"),
        ("THREAT LEVEL", "MINIMAL", "SAFE"),
        ("DATA FLOW", "4.2 GB/s", "STABLE")
    ]
    
    for label, val, status in stats:
        st.markdown(f"""
            <div style='margin-bottom:20px;'>
                <small style='color:#8892b0; display:block;'>{label}</small>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <span style='font-size:22px; font-weight:bold; color:white;'>{val}</span>
                    <span style='color:#64ffda; font-size:12px;'>● {status}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("DEPLOY SYSTEM INTELLIGENCE", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -- Center Panel: Core Nexus & Earth --
with col_center:
    st.markdown('<div class="nexus-portal">', unsafe_allow_html=True)
    
    # Large Si Image/Brand Centering
    if os.path.exists('logo_nexus.png'):
        st.image('logo_nexus.png', width=450)
    else:
        st.markdown('<h1 class="si-brand-text">Si</h1>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center; color:#ffd700; letter-spacing:4px; font-weight:300;'>SYSTEM INTELLIGENCE CORE</h2>", unsafe_allow_html=True)
    
    # 3D Animated Globe
    st.plotly_chart(create_global_map(), use_container_width=True)

# -- Right Panel: Operations Control --
with col_right:
    st.markdown('<div class="panel-container">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#64ffda; margin-top:0;'>OPERATIONS</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 0.5px solid rgba(100, 255, 218, 0.2);'>", unsafe_allow_html=True)
    
    st.markdown("<div><span class='status-pulse'></span><span style='color:#64ffda;'>SYSTEM OPTIMAL</span></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("Profit Optimization Index")
    st.progress(87)
    
    st.write("Efficiency Allocation")
    st.progress(91)
    
    st.markdown("<br><p style='color:#8892b0; font-size:12px;'>LIVE TRANSACTION FEED</p>", unsafe_allow_html=True)
    logs = ["SYNCING NODE-US...", "OPTIMIZING PK-CN FLOW...", "ENCRYPTING HUB-BR..."]
    for log in logs:
        st.code(log, language="bash")
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. FOOTER ---
st.markdown("<br><p style='text-align:center; opacity:0.3; font-size:10px;'>GLOBAL SYSTEM INTELLIGENCE V3.0 | SECURE CONNECTION ESTABLISHED</p>", unsafe_allow_html=True)
