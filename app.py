import streamlit as st
import os
import random
import time
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="System Intelligence | Ahsan Khan", layout="wide", page_icon="💠")

# --- Links & Pricing Details ---
basic_doc_url = "https://ahsankhan.lemonsqueezy.com/checkout/buy/ba3a76f7-4acc-4643-a838-9dc4085af6dc"
premium_doc_url = "https://ahsankhan.lemonsqueezy.com/checkout/buy/6245738f-4d29-4a0a-a574-e9a0e8838124"
website_url = "https://www.ahsanoranalyst.online/"
whatsapp_url = "https://wa.me/923245277654"

# 2. Advanced UI Styling (Enhanced CSS)
st.markdown(f"""
    <style>
    /* Main App Background with Moving Grid Effect */
    .stApp {{
        background: radial-gradient(circle at top right, #0a192f, #020c1b);
        background-attachment: fixed;
        color: #ccd6f6;
    }}
    
    /* System Log Styling */
    .system-log {{
        background: rgba(0, 0, 0, 0.5);
        border-left: 2px solid #64ffda;
        padding: 10px;
        font-family: 'Courier New', monospace;
        font-size: 10px;
        color: #64ffda;
        margin-top: 20px;
        border-radius: 5px;
    }}

    /* --- SIDEBAR BUTTONS --- */
    .sidebar-btn {{
        text-decoration: none;
        display: block;
        border: 1px solid #64ffda;
        padding: 12px;
        text-align: center;
        border-radius: 10px;
        color: white !important;
        font-weight: bold;
        margin-bottom: 12px;
        transition: 0.3s all ease-in-out;
        background: rgba(100, 255, 218, 0.05);
    }}
    .sidebar-btn:hover {{
        background-color: #64ffda !important;
        color: #020c1b !important;
        box-shadow: 0 0 25px #64ffda;
        transform: translateY(-2px);
    }}

    /* --- INDUSTRY CARDS (Enhanced) --- */
    .portal-box {{
        background: linear-gradient(145deg, #112240, #0a192f);
        border: 1px solid rgba(100, 255, 218, 0.3);
        padding: 20px;
        border-radius: 15px 15px 0px 0px;
        text-align: center;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: 0.4s;
    }}
    .portal-box:hover {{
        border-color: #64ffda;
        background: #1d3359;
    }}

    /* --- PRICING SECTION --- */
    .pricing-card {{
        background: #112240; padding: 40px; border-radius: 25px; text-align: center;
        height: 620px; transition: 0.4s;
    }}
    .pricing-card:hover {{ transform: scale(1.01); }}
    
    .basic-card {{ border: 3px solid #bdc3c7 !important; box-shadow: 0 0 15px rgba(189, 195, 199, 0.2); }}
    .premium-card {{ border: 3px solid #ffd700 !important; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2); }}

    .deploy-btn {{
        display: block; padding: 15px; border-radius: 12px; text-decoration: none !important;
        font-weight: 900; text-align: center; transition: 0.4s; margin-top: 20px;
    }}
    .basic-btn {{ border: 2px solid #bdc3c7; color: white !important; background: rgba(255,255,255,0.05); }}
    .premium-btn {{ border: 2px solid #ffd700; color: #ffd700 !important; background: rgba(255, 215, 0, 0.05); }}
    </style>
""", unsafe_allow_html=True)

# 3. State & Mapping
if 'selected_industry' not in st.session_state:
    st.session_state.selected_industry = None

industries = ["Agricultural", "Airline", "Bank", "Construction", "Diplomacy", "E-Commerce", "Education", "Energy Company", "Food Service", "Healthcare", "Hotel", "Insurance", "Manufacturing", "Military & Defense", "Pharmaceutical", "Real Estate", "Retail Chain", "Shipping Company", "Telecommunication", "Transmission", "Transportation"]

industry_map = {
    "Agricultural": "AGRI", "Airline": "AIRL", "Bank": "BANK", "Construction": "CONS",
    "Diplomacy": "DIPL", "E-Commerce": "ECOM", "Education": "EDUC", "Energy Company": "ENER",
    "Food Service": "FOOD", "Healthcare": "HEAL", "Hotel": "HOTE", "Insurance": "INSU",
    "Manufacturing": "MANU", "Military & Defense": "MILI", "Pharmaceutical": "PHAR",
    "Real Estate": "REAL", "Retail Chain": "RETA", "Shipping Company": "SHIP",
    "Telecommunication": "TELE", "Transmission": "TRANSM", "Transportation": "TRANSPO"
}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#64ffda;'>STRATEGIC CORE</h2>", unsafe_allow_html=True)
    
    st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="sidebar-btn">💬 WHATSAPP SUPPORT</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{website_url}" target="_blank" class="sidebar-btn">🌐 OFFICIAL WEBSITE</a>', unsafe_allow_html=True)
    st.markdown("---")
    
    # NEW FEATURE: System Intelligence Live Log
    st.markdown("<p style='font-size:10px; color:#64ffda;'>[LIVE SYSTEM LOG]</p>", unsafe_allow_html=True)
    log_msg = random.choice(["Syncing Neural Nodes...", "Optimizing Matrix...", "Analyzing Constraints...", "Building Logic Gates..."])
    st.markdown(f'<div class="system-log">> {log_msg}<br>> {datetime.now().strftime("%H:%M:%S")} - Active</div>', unsafe_allow_html=True)
    
    if st.session_state.selected_industry:
        prefix = industry_map.get(st.session_state.selected_industry, "NONE")
        st.markdown(f"<h3 style='color:#64ffda; text-align:center;'>📂 {st.session_state.selected_industry}</h3>", unsafe_allow_html=True)
        
        # --- DYNAMIC PROJECT LOADER ---
        if os.path.exists("pages"):
            files = sorted([f for f in os.listdir("pages") if f.upper().startswith(prefix)])
            st.markdown("<p style='color:#bdc3c7; font-weight:bold; font-size:10px;'>STANDARD ACCESS</p>", unsafe_allow_html=True)
            for f in files:
                if "PREM" not in f.upper():
                    name = f.replace(f"{prefix}_", "").replace(".py", "").replace("_", " ").title()
                    st.page_link(f"pages/{f}", label=f"🔓 {name}")
            
            st.markdown("<p style='color:#ffd700; font-weight:bold; font-size:10px; margin-top:15px;'>PREMIUM MODULES</p>", unsafe_allow_html=True)
            premium_found = False
            for f in files:
                if "PREM" in f.upper():
                    premium_found = True
                    name = f.replace(f"{prefix}_", "").replace("PREM_", "").replace(".py", "").replace("_", " ").title()
                    st.page_link(f"pages/{f}", label=f"🔒 {name} (Locked)")
            if not premium_found:
                st.markdown(f"<div style='font-size:12px; color:#ffd700;'>🔒 {st.session_state.selected_industry} Pro Optimizer</div>", unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🏠 Exit Command", use_container_width=True):
            st.session_state.selected_industry = None
            st.rerun()

# --- MAIN DASHBOARD ---
st.markdown("<h1 style='text-align:center; color:#64ffda; font-size:50px;'>SYSTEM INTELLIGENCE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ccd6f6; letter-spacing:3px;'>ADVANCED OPERATIONS RESEARCH ENGINE</p>", unsafe_allow_html=True)

if not st.session_state.selected_industry:
    # YouTube Video Restored
    video_id = "aDIUEaVF8v4"
    st.markdown(f'<div style="width: 100%; height: 350px; border-radius: 20px; border: 2px solid #64ffda; overflow: hidden; position: relative; margin-bottom: 30px;"><iframe style="position: absolute; top: -65px; left: 0; width: 100%; height: calc(100% + 130px); pointer-events: none;" src="https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&playlist={video_id}&controls=0" frameborder="0"></iframe></div>', unsafe_allow_html=True)

    # Industry Grid
    for i in range(0, len(industries), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(industries):
                name = industries[i+j]
                with cols[j]:
                    st.markdown(f'<div class="portal-box"><div style="color:white; font-size:20px; font-weight:900;">{name}</div><div style="color:#64ffda; font-size:11px; font-weight:bold;">LOAD CORE LOGIC</div></div>', unsafe_allow_html=True)
                    if st.button(f"Deploy Strategy", key=f"btn_{i+j}", use_container_width=True):
                        st.session_state.selected_industry = name
                        st.rerun()

# --- PRICING SECTION ---
st.markdown("<br><h2 style='text-align:center; color:white;'>System License Deployment</h2>", unsafe_allow_html=True)
p1, p2 = st.columns(2, gap="large")

with p1:
    st.markdown(f"""
    <div class="pricing-card basic-card">
        <div>
            <h3 style="color:#bdc3c7;">STANDARD CORE</h3>
            <div style="font-size: 32px; color: white; font-weight: bold;">$116</div>
            <p style="color:#64ffda;">Save 23% Today</p>
            <ul style="color:white; text-align:left; list-style:none; padding:0; font-size:14px; line-height:2.8;">
                <li>✔ Essential OR Models</li><li>✔ Resource Management Core</li><li>✔ Standard Analytics</li>
                <li>✔ Up to 5 Active Projects</li><li style="color:#bdc3c7;">✖ Full Library Access</li>
            </ul>
        </div>
        <a href="{basic_doc_url}" target="_blank" class="deploy-btn basic-btn">ACTIVATE BASIC</a>
    </div>
    """, unsafe_allow_html=True)

with p2:
    st.markdown(f"""
    <div class="pricing-card premium-card">
        <div>
            <h3 style="color:#ffd700;">ENTERPRISE UNLIMITED</h3>
            <div style="font-size: 32px; color: white; font-weight: bold;">$399</div>
            <p style="color:#ffd700;">Complete Control - Save 27%</p>
            <ul style="color:white; text-align:left; list-style:none; padding:0; font-size:14px; line-height:2.8;">
                <li>✔ 2100+ Optimization Projects</li><li>✔ Real-time Logistics Neural Sync</li><li>✔ 24/7 Human-Analyst Support</li>
                <li>✔ Custom Brand Integration</li><li style="color:#ffd700; font-weight:bold;">💎 Lifetime Full Access</li>
            </ul>
        </div>
        <a href="{premium_doc_url}" target="_blank" class="deploy-btn premium-btn">ACTIVATE PREMIUM</a>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown(f"<br><p style='text-align:center; font-size:12px; color:#444;'>Architected by Ahsan Khan | © {datetime.now().year} System Intelligence Group</p>", unsafe_allow_html=True)
