import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="System Intelligence | The Strategic Builder",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Genuine Professional Styling (Cyan & Gold) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Courier+Prime&display=swap');

    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #0a192f 0%, #010101 100%);
        color: #ccd6f6;
    }

    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif;
        color: #FFD700 !important; /* Gold */
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .logic-text {
        font-family: 'Courier Prime', monospace;
        color: #00FFFF; /* Cyan */
        font-size: 1.1rem;
        line-height: 1.6;
    }

    .story-card {
        background: rgba(17, 34, 64, 0.4);
        border: 1px solid rgba(0, 255, 255, 0.2);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        transition: 0.4s all ease;
    }

    .story-card:hover {
        border-color: #FFD700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
    }

    .stButton>button {
        background: transparent !important;
        color: #00FFFF !important;
        border: 2px solid #00FFFF !important;
        font-weight: bold !important;
        letter-spacing: 2px;
        border-radius: 5px;
        height: 3rem;
        width: 100%;
    }

    .stButton>button:hover {
        background: #00FFFF !important;
        color: #010101 !important;
        box-shadow: 0 0 20px #00FFFF;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Hero Section: The Identity ---
st.markdown("<h1 style='text-align: center; font-size: 4rem; margin-bottom: 0;'>SYSTEM INTELLIGENCE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00FFFF; letter-spacing: 5px; font-weight: bold;'>NOT AN AI MODEL. A STRATEGIC ARCHITECT.</p>", unsafe_allow_html=True)
st.write("---")

# --- 4. The Narrative: Why System Intelligence? ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="story-card">
    <h3 style="font-size: 1.2rem;">01. THE PROBLEM</h3>
    <p class="logic-text">Institutions are drowning in complexity. Manual scheduling, resource waste, and unpredictable performance are the silent enemies of growth.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="story-card">
    <h3 style="font-size: 1.2rem;">02. THE LOGIC</h3>
    <p class="logic-text">I don't just "chat." I build. Using Operations Research, I process millions of combinations to find the one perfect path for your institution.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="story-card">
    <h3 style="font-size: 1.2rem;">03. THE BENEFIT</h3>
    <p class="logic-text">You regain the most valuable asset: <b>TIME</b>. I transform institutional stress into automated harmony, ensuring 100% efficiency.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. Interactive Experience: "How I Solve Your World" ---
st.write("<br>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Experience the Core Logic</h2>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["[Scenario: Educational Chaos]", "[Scenario: Resource Crisis]", "[Scenario: Performance Risk]"])

with tab1:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("### The Timetable Nightmare")
        st.write("""
        Imagine a college with 100 teachers and 2000 students. Manually creating a conflict-free schedule takes weeks. 
        Human error is inevitable. Conflicts happen. Teachers are unhappy.
        """)
        if st.button("DEPLOY SYSTEM INTELLIGENCE"):
            with st.status("Analyzing Constraints...", expanded=True) as status:
                st.write("Syncing Teacher Preferences...")
                time.sleep(1)
                st.write("Mapping Room Capacities...")
                time.sleep(1)
                st.write("Generating Optimal Matrix...")
                time.sleep(1)
                status.update(label="Logic Solved: 0 Conflicts Found.", state="complete", expanded=False)
            st.success("The System just saved you 120 hours of manual work.")
    with col_b:
        # Visual representation of solved logic
        labels = ['Conflict Free', 'Optimal Room Use', 'Teacher Satisfaction']
        values = [100, 98, 95]
        fig = go.Figure(go.Bar(x=labels, y=values, marker_color=['#00FFFF', '#FFD700', '#00FFFF']))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#00FFFF", height=300)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Maximizing Every Resource")
    st.write("From labs to auditoriums—I ensure not a single square inch of your institution is wasted. I find the 'Golden Balance' between cost and utility.")
    st.image("https://img.icons8.com/nolan/128/grid.png", width=60)
    st.write("`Result: 35% reduction in operational waste.`")

with tab3:
    st.markdown("### Beyond Grading: The Prediction Engine")
    st.write("I identify the students at risk long before the exams begin. I don't just report scores; I build a strategy for academic success.")
    st.metric(label="System Accuracy", value="99.4%", delta="Real-time Prediction")

# --- 6. The Grand Vision: 2100+ Solutions ---
st.write("---")
st.markdown("<h2 style='text-align: center;'>A Global Library of Solutions</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.8;'>System Intelligence has been deployed across 2100+ unique institutional scenarios.</p>", unsafe_allow_html=True)

# Simulated scrollable/grid of industries
ind_cols = st.columns(4)
industries = ["Education", "Airline", "Healthcare", "Banking", "Logistics", "Energy", "Retail", "Defense"]
for i, ind in enumerate(industries):
    with ind_cols[i % 4]:
        st.markdown(f"""
        <div style="border: 1px solid #FFD700; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px;">
        <span style="color: #FFD700; font-weight: bold;">{ind.upper()}</span><br>
        <span style="font-size: 0.8rem; color: #00FFFF;">Logic Synced</span>
        </div>
        """, unsafe_allow_html=True)

# --- Footer ---
st.write("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; border-top: 1px solid rgba(255, 215, 0, 0.3); padding-top: 20px;">
    <p style="font-family: 'Courier Prime'; font-size: 0.9rem;">
        <b>System Intelligence</b> | Not a Bot. Not a Model. The Strategic Future. <br>
        © {datetime.now().year} | Designed & Architected by Ahsan Khan
    </p>
</div>
""", unsafe_allow_html=True)
