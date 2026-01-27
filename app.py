

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# --- 1. SETTINGS ---
ACTIVATION_KEY = "PAK-2026"
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {"Section A": [], "Section B": []}

# --- 2. THE LOGIC ENGINE (THE HEART OF THE APP) ---
def get_recommendations():
    sections = st.session_state.data_store["Section A"]
    teachers = st.session_state.data_store["Section B"]
    
    if not sections or not teachers:
        return "Need more data in both Section A and B to suggest matches."

    # Calculate Class Difficulty (Higher students + Special needs = High Difficulty)
    class_df = pd.DataFrame(sections)
    class_df['Difficulty'] = (class_df['Students'] * 0.5) + (class_df['Special Needs'] * 5)
    
    # Calculate Teacher Strength (Experience + Degree)
    teach_df = pd.DataFrame(teachers)
    qual_map = {"PhD": 30, "Masters": 20, "Bachelors": 10, "Other": 5}
    teach_df['Strength'] = (teach_df['Experience'] * 2) + teach_df['Degree'].map(qual_map)

    # Sorting to match the best with the most challenging
    class_sorted = class_df.sort_values(by='Difficulty', ascending=False)
    teach_sorted = teach_df.sort_values(by='Strength', ascending=False)

    matches = []
    for i in range(min(len(class_sorted), len(teach_sorted))):
        c_name = f"{class_sorted.iloc[i]['Grade']} ({class_sorted.iloc[i]['Section']})"
        t_name = teach_sorted.iloc[i]['Teacher']
        matches.append(f"✅ Suggestion: Assign **{t_name}** to **{c_name}** (High Priority Match)")
    
    return matches

# --- 3. MAIN INTERFACE ---
if not st.session_state.authenticated:
    st.title("🔐 Enterprise Resource Portal")
    key = st.text_input("Activation Key", type="password")
    if st.button("Activate"):
        if key == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
else:
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Go to", ["Section A: Student Load", "Section B: Teacher Profile", "AI Smart Match"])

    # (Previous Section A & B code remains the same as before...)
    if menu == "Section A: Student Load":
        st.subheader("Add Class/Student Data")
        with st.form("a_form", clear_on_submit=True):
            g = st.selectbox("Grade", [f"Grade {i}" for i in range(1,13)])
            s = st.text_input("Section")
            stds = st.number_input("Students", min_value=1)
            sp = st.number_input("Special Needs", min_value=0)
            if st.form_submit_button("Add Class"):
                st.session_state.data_store["Section A"].append({"Grade": g, "Section": s, "Students": stds, "Special Needs": sp})
                st.rerun()

    elif menu == "Section B: Teacher Profile":
        st.subheader("Add Teacher Expertise")
        with st.form("b_form", clear_on_submit=True):
            t = st.text_input("Teacher Name")
            q = st.selectbox("Degree", ["PhD", "Masters", "Bachelors", "Other"])
            e = st.number_input("Experience (Years)", min_value=0)
            if st.form_submit_button("Add Teacher"):
                st.session_state.data_store["Section B"].append({"Teacher": t, "Degree": q, "Experience": e})
                st.rerun()

    # --- THE NEW MATCHING PAGE ---
    elif menu == "AI Smart Match":
        st.title("🧠 AI Resource Recommendation")
        st.write("This engine analyzes teacher seniority and class difficulty to suggest the best placement.")
        
        recs = get_recommendations()
        
        if isinstance(recs, list):
            for r in recs:
                st.success(r)
            
            # Show Analysis Table
            st.write("### Data Analysis View")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Class Load (Difficulty)**")
                st.write(pd.DataFrame(st.session_state.data_store["Section A"]))
            with col2:
                st.write("**Teacher Capability (Strength)**")
                st.write(pd.DataFrame(st.session_state.data_store["Section B"]))
        else:
            st.warning(recs)

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
