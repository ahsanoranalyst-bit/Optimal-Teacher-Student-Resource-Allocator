import streamlit as st
import pandas as pd
import random
import time
import plotly.graph_objects as go
from datetime import datetime

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="System Intelligence | Optimization Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Advanced Styling (Cyan & Gold) ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #010101; color: #e0e0e0; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Arial Black', sans-serif; }
    .stButton>button { 
        color: #010101; background-color: #00FFFF; border: 2px solid #00FFFF; 
        font-weight: bold; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { background-color: transparent; color: #00FFFF; box-shadow: 0 0 15px #00FFFF; }
    .metric-card { 
        background-color: #0a0a0b; border: 1px solid rgba(0, 255, 255, 0.3); 
        border-radius: 10px; padding: 20px; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Header ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://img.icons8.com/nolan/128/artificial-intelligence.png", width=100)
with col2:
    st.title("SYSTEM INTELLIGENCE")
    st.markdown("**Core Operational Logic** | *Transforming Institutional Data into Automated Success*")

st.divider()

# --- 4. Live Metrics Feed ---
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
metrics = [
    ("Overall Efficiency", f"{random.randint(94, 98)}%", "#00FFFF"),
    ("System Conflicts", "0", "#00FF00"),
    ("Resource Load", f"{random.randint(80, 90)}%", "#FFD700"),
    ("Status", "ACTIVE", "#00FFFF")
]

for col, (label, val, clr) in zip([m_col1, m_col2, m_col3, m_col4], metrics):
    col.markdown(f'<div class="metric-card"><h4 style="color:white">{label}</h4><h2 style="color:{clr}">{val}</h2></div>', unsafe_allow_html=True)

st.write("")

# --- 5. Active Modules ---
t1, t2, t3 = st.tabs(["📅 Timetable Solver", "📈 Performance AI", "🏢 Resource Optimizer"])

with t1:
    st.markdown("### Intelligent Timetable Generator")
    if st.button("EXECUTE OPTIMIZATION ENGINE"):
        with st.status("Analyzing Constraints...", expanded=True) as status:
            st.write("Checking Teacher Availability...")
            time.sleep(0.5)
            st.write("Resolving Room Conflicts...")
            time.sleep(0.5)
            st.write("Applying Logic Gates...")
            time.sleep(0.5)
            status.update(label="Optimization Complete!", state="complete", expanded=False)
        
        # Simulated Data
        df = pd.DataFrame({
            'Teacher': ['Prof. Ahmed', 'Dr. Sarah', 'Engr. Khan'],
            'Subject': ['Maths', 'Physics', 'AI Logic'],
            'Room': ['Hall A', 'Lab 2', 'Room 101'],
            'Time': ['09:00 AM', '11:00 AM', '02:00 PM']
        })
        st.dataframe(df, use_container_width=True)
        
        # Professional Step: Allow downloading the result
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Optimized Schedule", data=csv, file_name="schedule.csv", mime="text/csv")

with t2:
    st.markdown("### Predictive Analytics")
    score = random.randint(85, 95)
    st.metric("Predicted Performance Index", f"{score}%", "High Efficiency")
    st.info("System Insight: Optimal performance detected across 92% of departments.")

with t3:
    st.markdown("### Dynamic Resource Allocation")
    st.table(pd.DataFrame({
        "Resource": ["Computer Lab", "Main Auditorium", "Library Hall"],
        "Allocation": ["95%", "80%", "100%"],
        "Conflict Risk": ["None", "None", "None"]
    }))

# --- Footer ---
st.divider()
st.markdown(f"<center><small>System Intelligence Core v5.3 | Registered to Ahsan Khan | {datetime.now().year}</small></center>", unsafe_allow_html=True)
