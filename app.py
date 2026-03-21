import streamlit as st
import time
import random

# 1. Page Configuration
st.set_page_config(page_title="System Intelligence | The Core Logic", layout="wide", page_icon="💠")

# --- Styling & Secret Aesthetic ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');

    .stApp {
        background: #010101; /* Deep Black for Mystery */
        color: #ccd6f6;
    }

    /* Secret Glow for Headings */
    .glitch-title {
        color: #ffd700;
        font-family: 'Arial Black', sans-serif;
        font-size: 50px;
        text-align: center;
        text-shadow: 0 0 10px #ffd700, 0 0 20px rgba(255, 215, 0, 0.5);
        margin-bottom: 0px;
    }

    .secret-tag {
        color: #64ffda;
        font-family: 'Courier Prime', monospace;
        text-align: center;
        font-size: 14px;
        letter-spacing: 5px;
        margin-bottom: 40px;
    }

    /* Narrative Cards */
    .story-card {
        background: rgba(17, 34, 64, 0.6);
        border: 1px solid #64ffda;
        padding: 30px;
        border-radius: 15px;
        font-family: 'Courier Prime', monospace;
        transition: 0.4s;
    }
    .story-card:hover {
        border-color: #ffd700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
    }

    /* Button Styling */
    .stButton>button {
        background: transparent !important;
        color: #64ffda !important;
        border: 2px solid #64ffda !important;
        font-weight: bold !important;
        height: 50px;
        width: 100%;
    }
    .stButton>button:hover {
        background: #64ffda !important;
        color: #010101 !important;
        box-shadow: 0 0 15px #64ffda;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown('<h1 class="glitch-title">SYSTEM INTELLIGENCE</h1>', unsafe_allow_html=True)
st.markdown('<p class="secret-tag">UNSEEN LOGIC // INFINITE SOLUTIONS</p>', unsafe_allow_html=True)

# --- The Story: What is it? ---
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### 🔍 The Secret Identity")
    st.markdown("""
    <div class="story-card">
    <b>System Intelligence is NOT a model.</b><br><br>
    It is a hidden layer of mathematical certainty. While others see chaos in schedules, 
    resources, and performance, I see patterns. I am the <b>Strategic Builder</b> 
    that sits behind your institution, silently constructing the most efficient 
    version of your reality.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### 💎 The Human Benefit")
    st.markdown("""
    <div class="story-card">
    <b>I don't just calculate; I empower.</b><br><br>
    By removing the burden of manual decision-making, I give you the most valuable 
    resource: <b>Time.</b> I transform institutional stress into operational 
    harmony, ensuring every teacher, student, and resource is exactly where they 
    need to be for maximum success.
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- Interactive "Core Discovery" ---
st.markdown("<h2 style='text-align:center; color:#ffd700;'>Discover the Impact</h2>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    with st.expander("🛡️ Strategic Defense"):
        st.write("I protect your institution from resource wastage and scheduling conflicts before they even happen.")
with c2:
    with st.expander("🚀 Performance Acceleration"):
        st.write("By predicting academic risks, I allow you to act when it matters most, not when it's too late.")
with c3:
    with st.expander("⚖️ Balanced Allocation"):
        st.write("Total equity in resource distribution, driven by pure logic, leaving no room for human error.")

st.write("<br>", unsafe_allow_html=True)

# --- Call to Action ---
st.markdown("""
    <div style="text-align:center; padding: 40px; border: 1px dashed #ffd700; border-radius: 20px;">
        <h4 style="color: #64ffda;">Ready to deploy the unseen logic?</h4>
        <p>System Intelligence is ready to build your success story.</p>
    </div>
""", unsafe_allow_html=True)

if st.button("INITIALIZE SYSTEM SYNC"):
    with st.status("Accessing Core Logic...", expanded=True) as status:
        st.write("Analyzing institutional variables...")
        time.sleep(1)
        st.write("Building optimization paths...")
        time.sleep(1)
        st.write("Strategy Generation: COMPLETE.")
        status.update(label="System Intelligence Active!", state="complete", expanded=False)
    st.balloons()

# Footer
st.markdown("<br><p style='text-align:center; font-size:12px; opacity:0.5;'>The identity of your success is System Intelligence. Built by Ahsan Khan.</p>", unsafe_allow_html=True)
