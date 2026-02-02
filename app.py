

import streamlit as st
import pandas as pd
from fpdf import FPDF

# --- 1. CORE INITIALIZATION ---
ACTIVATION_KEY = "PAK-2026"

# Ensure all keys exist in session state to avoid KeyErrors
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Grades_Config": {}, # Dictionary to store Subjects per Class-Section
        "A": [], # Student Grades
        "B": [], # Teacher Profiles
        "C": [], # Efficiency Mapping
        "School_Name": ""
    }

# --- 2. PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        name = st.session_state.data_store.get("School_Name", "SCHOOL REPORT")
        self.cell(0, 10, name.upper(), 0, 1, 'C')
        self.ln(5)

def create_pdf(data):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    pdf.set_font('Arial', 'B', 10)
    if not df.empty:
        col_width = 190 / len(df.columns)
        for col in df.columns: pdf.cell(col_width, 10, str(col), 1)
        pdf.ln()
        pdf.set_font('Arial', '', 9)
        for _, row in df.iterrows():
            for val in row: pdf.cell(col_width, 10, str(val), 1)
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI LOGIC ---

# Step 1: Activation
if not st.session_state.authenticated:
    st.title("🔐 Secure Activation")
    key_input = st.text_input("Enter System Key", type="password")
    if st.button("Activate System"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid Access Key")

# Step 2: Grade & Section Setup
elif not st.session_state.setup_complete:
    st.title("⚙️ School Configuration")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "My Institution")
    
    st.subheader("Define Class, Section & Subjects")
    c1, c2 = st.columns(2)
    g_name = c1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
    s_name = c2.text_input("Section (e.g., A, B, Blue, Green)")
    
    sub_input = st.text_area("Enter Subjects (comma separated)", "Math, English, Science")
    
    if st.button("Add This Class Configuration"):
        if s_name:
            full_key = f"{g_name}-{s_name}"
            subjects = [s.strip() for s in sub_input.split(",") if s.strip()]
            st.session_state.data_store["Grades_Config"][full_key] = subjects
            st.success(f"Added {full_key} with {len(subjects)} subjects.")
        else:
            st.warning("Please enter a Section name.")
    
    st.write("Current Setup:", st.session_state.data_store["Grades_Config"])
    
    if st.session_state.data_store["Grades_Config"] and st.button("Finalize & Go to Dashboard"):
        st.session_state.setup_complete = True
        st.rerun()

# Step 3: Main Application
else:
    st.sidebar.title(st.session_state.data_store["School_Name"])
    nav = st.sidebar.selectbox("Menu", 
        ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    # SECTION A: Student Data
    if nav == "Student Performance (A)":
        st.header("📊 Input Student Grades")
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        sel_class = st.selectbox("Select Class-Section", class_list)
        sel_sub = st.selectbox("Select Subject", st.session_state.data_store["Grades_Config"][sel_class])
        
        with st.form("a_form"):
            c1, c2, c3, c4 = st.columns(4)
            ga = c1.number_input("Grade A", 0)
            gb = c2.number_input("Grade B", 0)
            gc = c3.number_input("Grade C", 0)
            gd = c4.number_input("Grade D", 0)
            
            if st.form_submit_button("Save Data"):
                st.session_state.data_store["A"].append({
                    "Class": sel_class, "Subject": sel_sub, 
                    "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd
                })
                st.rerun()
        display_key = "A"

    # SECTION B: Teacher Data
    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Teacher Specialization")
        # Get all unique subjects defined in setup
        all_subs = set()
        for s_list in st.session_state.data_store["Grades_Config"].values():
            all_subs.update(s_list)
        
        with st.form("b_form"):
            t_name = st.text_input("Teacher Name")
            t_exp = st.selectbox("Specialization", list(all_subs))
            t_rate = st.slider("Past Success Rate (%)", 1, 100, 70)
            if st.form_submit_button("Add Teacher"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_rate})
                st.rerun()
        display_key = "B"

    # SECTION C: Mapping Logic
    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Efficiency & Allocation")
        if not st.session_state.data_store["A"] or not st.session_state.data_store["B"]:
            st.warning("Input Data in Section A & B first.")
        else:
            options = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
            sel = st.selectbox("Analyze Class Performance", options)
            
            # Find the data
            parts = sel.split(" | ")
            target_data = next(x for x in st.session_state.data_store["A"] if x['Class'] == parts[0] and x['Subject'] == parts[1])
            
            # Profit/Efficiency Logic (Scale 1-200)
            weak_students = (target_data['C'] * 1.2) + (target_data['D'] * 2.0)
            
            # Find matching teacher
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == parts[1]]
            if matches:
                best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                st.info(f"💡 Recommended: {best_t['Name']} for {parts[1]} (Expertise Score: {best_t['Success']}%)")
                
                if st.button("Confirm This Mapping"):
                    impact = min(200, (weak_students * (best_t['Success']/40)))
                    st.session_state.data_store["C"].append({
                        "Class": parts[0], "Subject": parts[1], "Teacher": best_t['Name'], "Impact_Score": round(impact, 2)
                    })
                    st.rerun()
            else:
                st.error("No expert teacher found for this subject.")
        display_key = "C"

    # --- SHARED DATA VIEW & DELETE ---
    if 'display_key' in locals() and st.session_state.data_store[display_key]:
        st.markdown("---")
        df = pd.DataFrame(st.session_state.data_store[display_key])
        st.dataframe(df, use_container_width=True)
        
        idx = st.selectbox("Select Record Index to Delete", df.index)
        col1, col2 = st.columns(2)
        if col1.button("🗑️ Delete Selected Record"):
            st.session_state.data_store[display_key].pop(idx)
            st.rerun()
        
        pdf_bytes = create_pdf(st.session_state.data_store[display_key])
        col2.download_button("📥 Download Report", pdf_bytes, f"{nav}.pdf")
