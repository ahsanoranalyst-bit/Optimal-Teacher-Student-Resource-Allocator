import streamlit as st
import os
import time
import random

# 1. Page Configuration
st.set_page_config(page_title="System Intelligence | Ahsan Khan", layout="wide", page_icon="💠")

# --- Links & Pricing Details ---
basic_doc_url = "https://ahsankhan.lemonsqueezy.com/checkout/buy/ba3a76f7-4acc-4643-a838-9dc4085af6dc"
premium_doc_url = "https://ahsankhan.lemonsqueezy.com/checkout/buy/6245738f-4d29-4a0a-a574-e9a0e8838124"
website_url = "https://www.ahsanoranalyst.online/"
whatsapp_url = "https://wa.me/923245277654"

# 2. Advanced UI Styling (CSS)
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');

    .stApp {{
        background: radial-gradient(circle at top right, #0a192f, #020c1b);
        color: #ccd6f6;
    }}
    
    /* System Intelligence Specific Font Styling */
    .logic-text {{
        font-family: 'Courier Prime', monospace;
        color: #64ffda;
        font-size: 16px;
        line-height: 1.6;
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: #112240 !important;
        border-right: 3px solid #64ffda;
    }}

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
    }}
    .sidebar-btn:hover {{
        background-color: #64ffda !important;
        color: #020c1b !important;
        box-shadow: 0 0 20px #64ffda;
    }}

    /* Master Glowing Effect */
    [data-testid="stSidebarNav"] ul li div a span {{
        color: #ffffff !important;
        font-weight: 800 !important;
        text-shadow: 0 0 5px rgba(100, 255, 218, 0.5);
    }}

    /* Pricing Card Animations */
    @keyframes silverPulse {{
        0% {{ border-color: #bdc3c7; box-shadow: 0 0 10px rgba(189, 195, 199, 0.3); }}
        50% {{ border-color: #ffffff; box-shadow: 0 0 25px rgba(255, 255, 255, 0.6); }}
        100% {{ border-color: #bdc3c7; box-shadow: 0 0 10px rgba(189, 195, 199, 0.3); }}
    }}
    @keyframes goldPulse {{
        0% {{ border-color: #ffd700; box-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }}
        50% {{ border-color: #ffaa00; box-shadow: 0 0 25px rgba(255, 170, 0, 0.5); }}
        100% {{ border-color: #ffd700; box-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }}
    }}

    .portal-box {{
        background: rgba(17,34,64,0.9);
        border: 2px solid #64ffda;
        padding: 20px;
        border-radius: 15px 15px 0px 0px;
        text-align: center;
        height: 110px;
    }}

    .pricing-card {{
        background: #112240; padding: 40px; border-radius: 25px; text-align: center;
        display: flex; flex-direction: column; justify-content: space-between;
        height: 600px;
    }}
    .basic-card {{ border: 3px solid #bdc3c7 !important; animation: silverPulse 3s infinite ease-in-out; }}
    .premium-card {{ border: 3px solid #ffd700 !important; animation: goldPulse 2.5s infinite ease-in-out; }}
    </style>
""", unsafe_allow_html=True)

# 3. State & Mapping
if 'selected_industry' not in st.session_state:
    st.session_state.selected_industry = None

industries = ["Agricultural", "Airline", "Bank", "Construction", "Diplomacy", "E-Commerce", "Education", "Energy Company", "Food Service", "Healthcare", "Hotel", "Insurance", "Manufacturing", "Military & Defense", "Pharmaceutical", "Real Estate", "Retail Chain", "Shipping Company", "Telecommunication", "Transmission", "Transportation"]

industry_map = {i: i[:4].upper() for i in industries} # Dynamic mapping

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#64ffda;'>CORE ENGINE</h2>", unsafe_allow_html=True)
    st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="sidebar-btn">💬 WHATSAPP SUPPORT</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{website_url}" target="_blank" class="sidebar-btn">🌐 OFFICIAL WEBSITE</a>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.selected_industry:
        st.markdown(f"<h3 style='color:#64ffda; text-align:center;'>📂 {st.session_state.selected_industry} Portal</h3>", unsafe_allow_html=True)
        # Project Loader Logic here (as per your original code)
        st.markdown("---")
        if st.button("🏠 Exit to Dashboard", use_container_width=True):
            st.session_state.selected_industry = None
            st.rerun()

# --- MAIN DASHBOARD ---
st.markdown("<h1 style='text-align:center; color:#64ffda; font-family:Arial Black;'>SYSTEM INTELLIGENCE</h1>", unsafe_allow_html=True)

if not st.session_state.selected_industry:
    # Neural Introduction Text (Typewriter Style Feel)
    st.markdown("""
    <div style='background: rgba(100, 255, 218, 0.05); padding: 20px; border-radius: 10px; border-left: 5px solid #64ffda; margin-bottom: 30px;'>
        <p class="logic-text">
        <b>[SYSTEM MESSAGE]:</b> I am the logic behind your success. Built on advanced <b>Operations Research</b>, 
        I analyze thousands of possibilities to find the perfect solution for your institution. 
        Experience the power of automated intelligence.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # YouTube Video 
    video_id = "aDIUEaVF8v4"
    st.markdown(f'<div style="width: 100%; height: 400px; border-radius: 20px; border: 3px solid #64ffda; overflow: hidden; position: relative; margin-bottom: 40px;"><iframe style="position: absolute; top: -65px; left: 0; width: 100%; height: calc(100% + 130px); pointer-events: none;" src="https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&playlist={video_id}&controls=0" frameborder="0"></iframe></div>', unsafe_allow_html=True)

    # Industry Grid
    for i in range(0, len(industries), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(industries):
                name = industries[i+j]
                with cols[j]:
                    st.markdown(f'<div class="portal-box"><div style="color:white; font-size:22px; font-weight:900;">{name}</div><div style="color:#64ffda; font-size:12px; font-weight:bold; margin-top:5px;">NEURAL ENGINE SYNC</div></div>', unsafe_allow_html=True)
                    if st.button(f"Access Intelligence Core", key=f"btn_{i+j}", use_container_width=True):
                        st.session_state.selected_industry = name
                        st.rerun()

# --- PRICING SECTION ---
st.markdown("<br><h2 style='text-align:center; color:white;'>Strategic License Deployment</h2>", unsafe_allow_html=True)
# (Pricing columns follow your original design)
