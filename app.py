import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import random

# --- 1. Page Configuration (Enterprise Grade) ---
st.set_page_config(
    page_title="System Intelligence | Operational Command",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Advanced UI/UX Styling (Cyan Diamond Theme) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=Montserrat:wght@700;900&display=swap');

    /* Main App Background */
    .stApp {{
        background-color: #010101; /* Deep Black */
        color: #ccd6f6;
    }}

    /* Title Styling (Montserrat & Gold/Cyan) */
    .command-title {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        font-size: 50px;
        color: #ffd700; /* Gold */
        text-align: center;
        text-shadow: 0 0 10px #ffd700, 0 0 20px rgba(255, 215, 0, 0.5);
    }}

    .command-subtitle {{
        font-family: 'Courier Prime', monospace;
        color: #64ffda; /* Cyan */
        text-align: center;
        font-size: 16px;
        letter-spacing: 4px;
        margin-top: -15px;
        margin-bottom: 30px;
    }}

    /* Card/Module Styling */
    .module-card {{
        background: rgba(17, 34, 64, 0.6);
        border: 2px solid #64ffda;
        padding: 25px;
        border-radius: 15px;
        font-family: 'Courier Prime', monospace;
        transition: 0.3s ease-in-out;
        height: 100%;
    }}
    .module-card:hover {{
        border-color: #ffd700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        transform: translateY(-5px);
    }}

    /* Professional Button Styling */
    .stButton>button {{
        background: transparent !important;
        color: #64ffda !important;
        border: 2px solid #64ffda !important;
        font-family: 'Courier Prime', monospace;
        font-weight: bold !important;
        border-radius: 8px;
        height: 50px;
        width: 100%;
        transition: 0.3s all;
    }}
    .stButton>button:hover {{
        background: #64ffda !important;
        color: #010101 !important;
        box-shadow: 0 0 20px #64ffda;
    }}

    /* Logo Placeholder Styling */
    .logo-container {{
        text-align: center;
        margin-bottom: -20px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. Header & Logo Integration ---
# (یہاں آپ اپنے جینون لوگو کا لنک ڈال سکتے ہیں)
# لوگو کا سائز اور اسٹائل آپ کے برانڈ کے مطابق سیٹ کیا گیا ہے
st.markdown("""
    <div class="logo-container">
        <img src="https://img.icons8.com/nolan/128/artificial-intelligence.png" width="100" style="filter: drop-shadow(0 0 10px #64ffda);"/>
    </div>
""", unsafe_allow_html=True)

st.markdown('<h1 class="command-title">SYSTEM INTELLIGENCE</h1>', unsafe_allow_html=True)
st.markdown('<p class="command-subtitle">ADVANCED OPERATIONS RESEARCH | NEURAL OPTIMIZATION</p>', unsafe_allow_html=True)
st.write("---")

# --- 4. The Core Logic: A Story of Optimization ---
# یہ سیکشن وزٹر کو بتاتا ہے کہ سسٹم محض ایک ماڈل نہیں بلکہ ایک 'بلڈر' ہے۔
st.subheader("🌐 The Strategic Builder: Beyond Common Logic")
st.markdown("""
    System Intelligence is a **Strategic Decision Builder**. It operates in the background, 
    deploying complex mathematics—specifically **Operations Research (OR)**—to solve 
    problems that are too intricate for human planning. 
    
    Whether it's the **Airline** industry managing complex flight paths or an **Educational 
    Institution** building impossible timetables, I transform raw constraints into 
    operational harmony. My purpose is to **maximize profit, minimize waste, and guarantee 
    certainty.**
""", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

# --- 5. Interactive Operation Rooms: Demonstrating Capabilities ---
# یہاں وزٹر دیکھ سکتا ہے کہ سسٹم الگ الگ انڈسٹریز میں کیسے کام کرتا ہے۔
st.subheader("🛠️ Active Operation Rooms")

tab1, tab2, tab3 = st.tabs(["[Module: Timetable Solving]", "[Module: Profit Maximizer]", "[Module: Risk Analytics]"])

# --- TAB 1: EDUCATIONAL TIMETABLE SOLVING (Logic Demo) ---
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("#### Problem Statement")
        st.markdown("""
            Build a conflict-free timetable for an institution with **200+ teachers, 
            50+ classrooms, and 5000+ students**, considering availability, subject 
            expertise, and travel time.
        """, unsafe_allow_html=True)
        st.info("Human Time: 2-3 Weeks | **System Intelligence Time: 15 Minutes**")
    
    with col2:
        st.markdown("#### Logic Execution (Simulated)")
        # Simulating the optimization process
        if st.button("EXECUTE TIMETABLE SOLVER"):
            with st.status("Initializing OR Algorithm...", expanded=True) as status:
                st.write("Fetching constraints (Availability, Rooms, Workload)...")
                time.sleep(1)
                st.write("Building the constraint matrix...")
                time.sleep(1)
                st.write("Solving the Integer Programming problem...")
                time.sleep(1)
                st.write("Optimization Complete: Conflict-Free Solution Generated.")
                status.update(label="System Solved!", state="complete", expanded=False)
            
            # Simulated Solution Data for visual impact
            data = {
                "Teacher ID": ["T101", "T101", "T102", "T103", "T104"],
                "Department": ["Math", "Math", "Physics", "Chemistry", "English"],
                "Subject": ["Calculus I", "Calculus II", "Mechanics", "Organic Chem", "Composition"],
                "Timeslot": ["09:00 - 10:30", "10:45 - 12:15", "13:00 - 14:30", "14:45 - 16:15", "09:00 - 10:30"],
                "Room": ["Auditorium A", "Room 302", "Room 301", "Auditorium B", "Room 101"]
            }
            st.success("Solved Schedule (Simulated Data):")
            st.dataframe(pd.DataFrame(data), use_container_width=True)

# --- TAB 2: GENERAL PROFIT MAXIMIZER (Financial Logic) ---
with tab2:
    st.markdown("#### Strategic Profit Allocation Model")
    st.markdown("""
        I analyze multiple revenue streams and resource costs to find the exact configuration 
        that **maximizes institutional profit** while minimizing operational expense.
    """, unsafe_allow_html=True)
    
    # Generate a professional-looking Plotly Pie Chart (Cyan/Gold)
    labels = ['Operational Cost', 'Reserved Funds', 'Net Profit']
    values = [4500, 1500, 9000] # Random professional looking numbers
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, marker_colors=['#444', '#ffd700', '#64ffda'])])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#64ffda", margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: NEURAL RISK ANALYTICS (Prediction Logic) ---
with tab3:
    st.markdown("#### Neural Network Risk Prediction")
    st.markdown("""
        I process thousands of historical data points to predict academic risk, identifying 
        students who need early intervention and transforming raw scores into smart decisions.
    """, unsafe_allow_html=True)
    
    # Gauge Chart for Risk (Silver/Gold Pulse look)
    risk_score = random.randint(75, 95)
    risk_level = "Medium" if risk_score < 80 else "Low"
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Predicted Average Score", 'font': {'size': 18, 'color': '#ffd700'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#ffd700"},
            'bar': {'color': "#64ffda"},
            'bgcolor': "#010101",
            'borderwidth': 2,
            'bordercolor': "rgba(100, 255, 218, 0.2)",
            'steps': [
                {'range': [0, 70], 'color': 'rgba(255, 75, 75, 0.2)'},
                {'range': [70, 85], 'color': 'rgba(255, 215, 0, 0.15)'},
                {'range': [85, 100], 'color': 'rgba(100, 255, 218, 0.1)'}
            ],
            'threshold': {
                'line': {'color': "#ffd700", 'width': 4},
                'thickness': 0.75,
                'value': risk_score
            }
        }
    ))
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20), height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

st.write("---")

# --- 6. The Industry Library (General & Professional Integration) ---
# یہ حصہ آپ کی بتائی ہوئی 2,100 انڈسٹری گریڈ لسٹ کو پروفیشنل طریقے سے دکھاتا ہے۔
st.subheader("📂 Strategic Solutions Library")
st.markdown("""
    My unseen logic has been deployed across **2000+ specialized projects** in diverse 
    global industries, creating certainty and efficiency wherever complexity exists.
""", unsafe_allow_html=True)

industries = ["Agricultural", "Airline", "Bank", "Construction", "Diplomacy", "E-Commerce", "Education", "Energy Company", "Food Service", "Healthcare", "Hotel", "Insurance", "Manufacturing", "Military & Defense", "Pharmaceutical", "Real Estate", "Retail Chain", "Shipping Company", "Telecommunication", "Transmission", "Transportation"]

# Grid layout for industries
cols = st.columns(4)
for i, name in enumerate(industries):
    with cols[i % 4]:
        st.markdown(f"""
            <div class="module-card">
                <span style="color:#ffd700; font-size:18px; font-weight:bold;">{name}</span><br>
                <span style="color:#64ffda; font-size:12px;">Operational Optimizer</span>
            </div>
        """, unsafe_allow_html=True)
        st.write("<br>", unsafe_allow_html=True)

# Footer
st.markdown("<br><p style='text-align:center; font-size:12px; opacity:0.6; font-family:Courier Prime;'>The identity of your institutional success is System Intelligence. Built by Ahsan Khan.</p>", unsafe_allow_html=True)
