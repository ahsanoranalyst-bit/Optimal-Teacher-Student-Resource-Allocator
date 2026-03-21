import streamlit as st
import pandas as pd
import random
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. Page Configuration (The very first Streamlit command) ---
st.set_page_config(
    page_title="System Intelligence | Optimization Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Professional Core Styling (Cyan & Gold) ---
# Custom CSS to apply the theme and make it look like a high-tech interface
st.markdown("""
<style>
    /* Main Background and Text */
    [data-testid="stAppViewContainer"] {
        background-color: #010101; /* Pure Black Background */
        color: #e0e0e0; /* Off-White Text */
    }
    [data-testid="stHeader"] {
        background: transparent;
    }

    /* Titles and Headers (Gold) */
    h1, h2, h3, h4, h5, h6 {
        color: #FFD700 !important; /* Metallic Gold */
        font-family: 'Arial Black', sans-serif;
    }

    /* Primary Accent Color (Cyan) for buttons and interactives */
    .stButton>button {
        color: #010101;
        background-color: #00FFFF; /* Pure Cyan */
        border: 2px solid #00FFFF;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: transparent;
        color: #00FFFF;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.7);
    }

    /* Data Containers (Cards) with Cyan Border */
    .stPlotlyChart {
        border: 1px solid rgba(0, 255, 255, 0.2);
        border-radius: 8px;
        padding: 5px;
        background-color: #0a0a0b;
    }
    .metric-card {
        background-color: #0a0a0b;
        border: 1px solid rgba(0, 255, 255, 0.2);
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Header and Initial System Information ---
# A clean top banner with a genuine description of the system's purpose.
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://img.icons8.com/nolan/128/artificial-intelligence.png", width=90) # Simple AI Icon
with col2:
    st.markdown("### SYSTEM INTELLIGENCE GROUP")
    st.markdown("""
        **Operational Excellence Platform** | Optimizing Institutional Performance
        ---
        *Welcome to the core logic engine. I am not just a program; I am the logic behind your success. 
        Built on advanced Operations Research, I transform raw data into smart, automated decisions.*
    """, unsafe_allow_html=True)
st.divider()

# --- 4. System Operational Status (Simulation) ---
# This simulates real-time data processing and optimization.
st.subheader("📡 Real-Time Optimization Feed")
st.markdown("<small>System status updated at <b>{}</b></small>".format(datetime.now().strftime("%H:%M:%S")), unsafe_allow_html=True)

# Function to simulate real-time performance update
def simulate_optimization_metrics():
    # Define metric ranges
    efficiency = random.randint(92, 98)
    conflicts = random.randint(0, 4)
    resource_use = random.randint(85, 95)
    
    # Choose color for efficiency (Cyan for good, Gold for attention)
    eff_color = "#00FFFF" if efficiency >= 95 else "#FFD700"
    
    # Display Metrics
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #FFD700;">Overall Efficiency</h4>
            <span style="font-size: 2.5em; font-weight: bold; color: {eff_color};">{efficiency}%</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #FFD700;">System Conflicts</h4>
            <span style="font-size: 2.5em; font-weight: bold; color: #ff4b4b;">{conflicts} <small style="font-size:0.5em;">(Active)</small></span>
        </div>
        """, unsafe_allow_html=True)

    with m_col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #FFD700;">Resource Utilization</h4>
            <span style="font-size: 2.5em; font-weight: bold; color: #00FFFF;">{resource_use}%</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #FFD700;">Optimization Tasks</h4>
            <span style="font-size: 2.5em; font-weight: bold; color: #00FFFF;">Active</span>
        </div>
        """, unsafe_allow_html=True)

# Run the metrics simulation once to fill the page
simulate_optimization_metrics()
st.divider()

# --- 5. Modular Workflows (What the System *Does*) ---
# Use Tabs for different work modules, making the dashboard organized.
st.subheader("🛠️ Active Decision Modules")

tab1, tab2, tab3 = st.tabs(["[Module 01: Teacher Timetable]", "[Module 02: Performance Predictor]", "[Module 03: Resource Allocation]"])

# --- TAB 1: TEACHER SCHEDULING (Optimization Logic Simulation) ---
with tab1:
    st.markdown("#### Teacher Timetable Optimization (Core OR Logic)")
    st.markdown("""
        *Solving the complex problem of assigning teachers to classes while adhering to thousands 
        of constraints (availability, workload, room capacity, subject expertise).*
    """, unsafe_allow_html=True)
    
    if st.button("RUN SCHEDULING OPTIMIZER"):
        with st.spinner("Processing constraints and solving the assignment problem..."):
            time.sleep(1.5) # Simulate processing
            
            # Simulated Solution Data
            solved_schedules = {
                'Teacher ID': ['T101', 'T101', 'T102', 'T103', 'T104', 'T105'],
                'Department': ['Math', 'Math', 'Physics', 'Chemistry', 'English', 'Computer Science'],
                'Subject': ['Calculus I', 'Calculus II', 'Mechanics', 'Organic Chemistry', 'Composition', 'Data Structures'],
                'Timeslot': ['09:00 - 10:30', '10:45 - 12:15', '13:00 - 14:30', '14:45 - 16:15', '09:00 - 10:30', '10:45 - 12:15'],
                'Optimal Room': ['Auditorium A', 'Room 302', 'Room 301', 'Auditorium B', 'Room 101', 'Lab 204']
            }
            schedule_df = pd.DataFrame(solved_schedules)
            
            st.success("Timetable solved with 98% efficiency and 0 primary conflicts.")
            
            # Display the result in a clean table (Streamlit native)
            st.dataframe(schedule_df, use_container_width=True)
            st.caption("Conflicts checked: Availability (OK), Room Cap (OK), Travel Time (OK), Max Workload (OK).")


# --- TAB 2: STUDENT ANALYTICS (Data Transformation Simulation) ---
with tab2:
    st.markdown("#### Student Performance & Risk Analytics")
    st.markdown("""
        *I analyze thousands of data points to predict academic risk, identifying students 
        who need early intervention and transforming raw scores into smart institutional decisions.*
    """, unsafe_allow_html=True)
    
    # Generate simulated data for a Gauge Chart (very professional)
    performance_score = random.randint(70, 90) # Out of 100
    risk_level = "Medium" if performance_score < 75 else "Low"
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Professional Gauge Chart (using Plotly) with Cyan and Gold accents
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = performance_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Predicted Average Grade", 'font': {'size': 20, 'color': '#FFD700'}},
            number = {'font': {'color': '#00FFFF'}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#FFD700"},
                'bar': {'color': "#00FFFF"}, # Main bar in Cyan
                'bgcolor': "#0a0a0b",
                'borderwidth': 2,
                'bordercolor': "rgba(0, 255, 255, 0.2)",
                'steps': [
                    {'range': [0, 70], 'color': 'rgba(255, 75, 75, 0.2)'}, # Red zone
                    {'range': [70, 85], 'color': 'rgba(255, 215, 0, 0.15)'}, # Gold/Yellow zone
                    {'range': [85, 100], 'color': 'rgba(0, 255, 255, 0.1)'} # Cyan zone
                ],
                'threshold': {
                    'line': {'color': "#FFD700", 'width': 4},
                    'thickness': 0.75,
                    'value': performance_score
                }
            }
        ))
        fig_gauge.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        st.markdown(f"**Calculated Academic Risk: <span style='color:#FFD700;'>{risk_level}</span>**", unsafe_allow_html=True)
        
        # A simple insight generated based on the prediction.
        if performance_score < 75:
            st.warning("Prediction insight: Students in the 'Department of Arts' show lower than expected average scores. Immediate intervention recommended.")
        else:
            st.success("Prediction insight: Performance is generally stable. Department-level efficiency is optimal.")
            
        st.markdown("---")
        st.markdown("#### Input Parameters for Analysis:")
        # Display inputs in a professional grid-like format
        st.markdown("`Previous Scores` / `Attendance Rate` / `Class Size` / `Teacher Exp` / `Resource Score`")
        st.markdown("`01/02/03` | `>90%` | `~30` | `~12Y` | `>80`")


# --- TAB 3: RESOURCE ALLOCATION (Optimization Logic Simulation) ---
with tab3:
    st.markdown("#### Dynamic Resource Allocation (Dynamic Programming Simulation)")
    st.markdown("""
        *Dynamically assigning limited resources (labs, specialized equipment, study halls) to departments 
        to ensure maximum utilization and zero conflict.*
    """, unsafe_allow_html=True)
    
    # Simple simulated logic for allocation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Optimized Allocation Matrix (Simulated)")
        # Create a sample list/matrix to display allocations.
        allocation_data = {
            'Resource': ['Comp. Lab A', 'Physics Lab B', 'Auditorium X', 'Room 101'],
            'Primary Alloc': ['CS Department', 'Engineering', 'Orientation (All)', 'English'],
            'Time (PM)': ['01:00-03:00', '10:00-12:00', '09:00-11:00', '12:00-02:00'],
            'Utilization': ['96%', '94%', '100%', '88%']
        }
        alloc_df = pd.DataFrame(allocation_data)
        st.dataframe(alloc_df, use_container_width=True)
        
    with col2:
        st.markdown("#### System Alerts")
        if random.random() > 0.5:
             st.info("System Alert: High demand detected for 'Comp. Lab A' for the next semester. Consider expansion planning.")
        else:
             st.success("All resource allocations optimized for current demand.")

# --- 6. Final Disclaimer / System Log ---
st.divider()
st.markdown("<small style='color: #444;'>[INTERNAL LOG] Core logic simulation running. Model version: OR_Core_05.3. All data displayed is illustrative. For genuine optimization results, connect to the primary data pipeline.</small>", unsafe_allow_html=True)
st.markdown("<small style='color: #444;'>Copyright © 2026 System Intelligence Group.</small>", unsafe_allow_html=True)

