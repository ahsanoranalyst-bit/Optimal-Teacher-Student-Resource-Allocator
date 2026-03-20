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

# --- 2. ADVANCED UI STYLING (CSS - Fixed, Large Logo, Text-in-Box) ---
st.markdown(f"""
    <style>
    /* Main App Background */
    .stApp {{
        background: radial-gradient(circle at center, #020c1b, #0a192f);
        color: #ccd6f6;
        font-family: 'Consolas', monospace;
    }}
    
    /* Center the main content */
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 95%;
    }}

    /* Global Glow Effects */
    h1, h2, h3, h4, p, span, div {{
        text-shadow: 0 0 5px rgba(100, 255, 218, 0.2);
    }}

    /* --- COMMON PANEL STYLING (Themed Boxes) --- */
    .cyan-panel {{
        background: rgba(17, 34, 64, 0.9);
        border: 2px solid #64ffda;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(100, 255, 218, 0.3);
    }}
    .gold-accent-panel {{
        border: 2px solid #ffd700;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
    }}

    /* --- NEW HEADER STYLING (Text IN BOX) --- */
    /* Place headers within a stylized, slightly indented inner box */
    .inner-panel-header {{
        background: rgba(100, 255, 218, 0.05);
        border: 1px solid rgba(100, 255, 218, 0.2);
        border-radius: 8px;
        color: white;
        text-align: center;
        padding: 10px;
        margin-top: -10px;
        margin-bottom: 25px;
        margin-left: -5px;
        margin-right: -5px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        box-shadow: inset 0 0 8px rgba(100, 255, 218, 0.1);
    }}
    .cyan-header {{ color: #64ffda !important; border-color: rgba(100, 255, 218, 0.4) !important; }}
    .gold-header {{ color: #ffd700 !important; border-color: rgba(255, 215, 0, 0.4) !important; background: rgba(255, 215, 0, 0.05) !important;}}

    /* --- PANEL ITEMS STYLING --- */
    /* Connected Nations List & Schedule List */
    .list-item {{
        background: rgba(100, 255, 218, 0.05);
        border: 1px solid rgba(100, 255, 218, 0.2);
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: 0.3s;
    }}
    .list-item:hover {{
        background: rgba(100, 255, 218, 0.1);
        border-color: #64ffda;
        transform: translateX(5px);
    }}

    .schedule-time {{ color: #ffd700; font-weight: bold; margin-right: 10px; font-size: 14px;}}
    .schedule-locs {{ color: white; font-size: 14px;}}
    .country-flag-label {{ display: flex; align-items: center; color: white; font-weight: bold; font-size: 14px; }}

    /* Real-Time Metrics */
    .metric-box {{
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.02);
        margin-bottom: 10px;
    }}
    .metric-value {{ font-size: 20px; font-weight: bold; color: white; }}
    .metric-label {{ font-size: 11px; color: #64ffda; text-transform: uppercase; }}

    /* System Health Bar */
    .health-bar-container {{
        width: 100%;
        background-color: #112240;
        border-radius: 10px;
        height: 12px;
        border: 1px solid #ffd700;
        margin-bottom: 15px;
    }}
    .health-bar {{
        height: 100%;
        background: linear-gradient(90deg, #64ffda, #ffd700);
        border-radius: 10px;
        width: 100%; /* Default Optimal */
    }}

    /* --- PARTICIPATING COUNTRIES MENU (IMAGE BASED) --- */
    .participating-banner-container {{
        text-align: center;
        background: rgba(17, 34, 64, 0.9);
        border: 2px solid #64ffda;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 15px rgba(100, 255, 218, 0.3);
    }}
    
    /* Center the banner image within the participating panel */
    .participating-image-wrapper {{
        display: flex;
        justify-content: center;
    }}

    /* --- FIXED BUTTON VISIBILITY (WHITE BOX ISSUE) --- */
    .stButton>button {{
        width: 100% !important;
        background-color: rgba(100, 255, 218, 0.1) !important;
        color: #64ffda !important;
        border: 1px solid #64ffda !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        height: 35px !important;
        font-size: 13px !important;
        letter-spacing: 1px;
    }}
    .stButton>button:hover {{
        background-color: #64ffda !important;
        color: #020c1b !important;
        box-shadow: 0 0 15px #64ffda;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
@st.cache_data
def get_world_coordinates():
    return {
        'PK': [69.3451, 30.3753], 'USA': [-95.7129, 37.0902], 'CN': [104.1954, 35.8617],
        'DE': [10.4515, 51.1657], 'UK': [-1.1743, 54.2379], 'BR': [-51.9253, -14.2350],
        'AU': [133.7751, -25.2744], 'UAE': [53.8478, 23.4241], 'SG': [103.8198, 1.3521]
    }

def generate_schedule_data():
    locs = get_world_coordinates()
    data = []
    for i in range(5):
        route = np.random.choice(list(locs.keys()), 2, replace=False)
        start_time = time.strftime("%H:%M", time.gmtime(time.time() - (i*900)))
        cargo_type = np.random.choice(["AGRI FEED", "PHARMA UNIT", "RETAIL GOODS", "ENERGY PART", "MILI TECH"])
        data.append({
            'time': f'[{start_time}]',
            'details': f'{cargo_type}: {route[0]} -> {route[1]}'
        })
    return data

# --- 4. TOP: PARTICIPATING COUNTRIES MENU (IMAGE BASED, IN BOX) ---
st.markdown('<div class="participating-banner-container">', unsafe_allow_html=True)
st.markdown('<div style="color:#64ffda; font-weight:bold; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px;">PARTICIPATING COUNTRIES (GLOBAL HUB)</div>', unsafe_allow_html=True)
st.markdown('<div class="participating-image-wrapper">', unsafe_allow_html=True)
try:
    # Use the image containing the participating country flags as the header
    country_banner = Image.open('logo_participating.png')
    # Use center alignment and scale down slightly for banner lco
    st.image(country_banner, use_column_width=False, output_format="PNG", width=800)
except FileNotFoundError:
    st.error("Error: 'logo_participating.png' not found. Please add the participating countries image banner.")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. MAIN CONTENT (GRID LAYOUT) ---
col_left, col_center, col_right = st.columns([1, 2, 1], gap="medium")

# --- LEFT PANEL: GLOBAL NETWORK INTELLIGENCE ---
with col_left:
    st.markdown('<div class="cyan-panel">', unsafe_allow_html=True)
    
    # 1. FIXED HEADER (Text IN BOX)
    st.markdown('<div class="inner-panel-header cyan-header">GLOBAL NETWORK INTELLIGENCE</div>', unsafe_allow_html=True)
    
    # 2. Connected Nations List
    st.markdown('<p style="color:#64ffda; font-weight:bold; letter-spacing:1px; margin-bottom:5px;">CONNECTED NATIONS LIST</p>', unsafe_allow_html=True)
    countries = [
        ("Pakistan", "🇵🇰", "PK"), ("China", "🇨🇳", "CN"), ("USA", "🇺🇸", "US"), 
        ("Germany", "🇩🇪", "DE"), ("UK", "🇬🇧", "UK"), ("Brazil", "🇧🇷", "BR"), 
        ("Australia", "🇦🇺", "AU")
    ]
    for name, flag, code in countries:
        st.markdown(f'''
            <div class="list-item">
                <span class="country-flag-label">{flag} &nbsp; <span style="color:#ffd700;">{code}</span> &nbsp; {name.upper()}</span>
                <span style="color:#64ffda; font-weight:bold;">•••</span>
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('<br>', unsafe_allow_html=True) # Spacer

    # 3. Performance Counters
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.markdown('<div class="metric-value">18ms</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">GLOBAL RESPONSE TIME</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.markdown('<div class="metric-value">99.999%</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">NETWORK UPTIME</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. Features (Themed Buttons)
    st.button("DEEP AI ANALYSIS", use_container_width=True)
    st.button("THREAT MITIGATION", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True) # End Cyan Panel

# --- CENTER PANEL: GLOBAL NEXUS GLOBAL FLOW VISUALIZATION ---
with col_center:
    st.markdown('<div class="cyan-panel gold-accent-panel" style="text-align:center;">', unsafe_allow_html=True)
    
    # 1. FIXED HEADER (Text IN BOX)
    st.markdown('<div class="inner-panel-header gold-header">GLOBAL NEXUS GLOBAL FLOW VISUALIZATION</div>', unsafe_allow_html=True)
    
    # 2. ENLARGED CENTRAL LOGO NEXUS (LARGE Si Cube)
    try:
        # Use the high-detail central emblem image
        nexus_logo = Image.open('logo_nexus.png')
        # Center the logo image and scale it up significantly (e.g., width=450)
        st.image(nexus_logo, width=450, output_format="PNG")
        st.markdown('<div style="color:#ffd700; font-weight:bold; font-size:16px; margin-top:-10px; margin-bottom: 20px; text-transform:uppercase; letter-spacing:1px;">SYSTEM INTELLIGENCE CORE NEXUS</div>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Error: 'logo_nexus.png' not found. Please add the central Si emblem logo.")

    #Spacer
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    # 3. THE GLOBAL DATA FLOW MAP (PLOTLY 3D Globe Visualization)
    locs = get_world_coordinates()
    central_hub = locs['PK']
    
    connections = [
        (central_hub, locs['CN']), (central_hub, locs['USA']), (central_hub, locs['DE']),
        (central_hub, locs['BR']), (central_hub, locs['AU']), (central_hub, locs['UAE'])
    ]

    fig = go.Figure()

    # Draw connection lines
    for start, end in connections:
        fig.add_trace(go.Scattergeo(
            locationmode = 'country names',
            lon = [start[0], end[0]],
            lat = [start[1], end[1]],
            mode = 'lines+markers',
            line = dict(width = 2, color = '#ffd700'), # Gold streams
            marker = dict(size = [5, 5], color = ['#64ffda', '#ffd700'], symbol = 'circle'), # Cyan -> Gold flow
            opacity = 0.6,
            name = f'Stream: {start} -> {end}'
        ))

    # Configure the 3D globe view
    fig.update_layout(
        geo = dict(
            projection_type = 'orthographic',
            showland = True,
            landcolor = '#020c1b',
            oceancolor = '#0a192f',
            showocean = True,
            showcountries = True,
            countrycolor = '#112240',
            bgcolor = 'rgba(0,0,0,0)',
            center=dict(lon=central_hub[0], lat=central_hub[1]), # Center on Pakistan Hub
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div style="color:#64ffda; font-weight:bold; font-size:12px; margin-top:-10px; text-transform:uppercase; letter-spacing:1.2px;">GLOBAL INTELLIGENCE NETWORK</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) # End Center Panel

# --- RIGHT PANEL: GLOBAL INTELLIGENCE DASHBOARD ---
with col_right:
    st.markdown('<div class="cyan-panel">', unsafe_allow_html=True)
    
    # 1. FIXED HEADER (Text IN BOX)
    st.markdown('<div class="inner-panel-header cyan-header">GLOBAL INTELLIGENCE NETWORK DASHBOARD</div>', unsafe_allow_html=True)
    
    # 2. Advantage Metrics
    st.markdown('<p style="color:#64ffda; font-weight:bold; letter-spacing:1px; margin-bottom:5px;">REAL-TIME ADVANTAGE METRICS</p>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f'''
            <div class="metric-box">
                <div class="metric-value">87%</div>
                <div class="metric-label">PROFIT OPTIMIZATION INDEX</div>
            </div>
        ''', unsafe_allow_html=True)
    with m2:
        st.markdown(f'''
            <div class="metric-box">
                <div class="metric-value">91%</div>
                <div class="metric-label">OPERATIONAL EFFICIENCY</div>
            </div>
        ''', unsafe_allow_html=True)
        
    #Spacer
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    # 3. System Health Bar
    st.markdown('<p style="color:#64ffda; font-weight:bold; letter-spacing:1px; margin-bottom:5px;">SYSTEM HEALTH: <span style="color:#ffd700;">OPTIMAL</span></p>', unsafe_allow_html=True)
    st.markdown('<div class="health-bar-container"><div class="health-bar"></div></div>', unsafe_allow_html=True)

    # Spacer
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    # 4. Global Schedule (dynamic data)
    st.markdown('<p style="color:#64ffda; font-weight:bold; letter-spacing:1px; margin-bottom:5px;">GLOBAL LOGISTICS NETWORK</p>', unsafe_allow_html=True)
    schedule_data = generate_schedule_data()
    for entry in schedule_data:
        st.markdown(f'''
            <div class="list-item">
                <span class="schedule-time">{entry['time']}</span>
                <span class="schedule-locs">{entry['details']}</span>
            </div>
        ''', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True) # End Cyan Panel

# --- 6. FOOTER SPACE (Optional) ---
st.markdown("<br><br>", unsafe_allow_html=True)
