https://g.co/gemini/share/c3131c467243 

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# --- 1. CONFIGURATION & LICENSE ---
ACTIVATION_KEY = "PAK-2026"
EXPIRY_DATE = date(2026, 12, 31)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'school_setup_done' not in st.session_state:
    st.session_state.school_setup_done = False
if 'school_name' not in st.session_state:
    st.session_state.school_name = ""
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Section A": [], "Section B": [], "Section C": [], "Section D": []
    }

# --- 2. PDF GENERATOR ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.school_name.upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 12)
        self.cell(0, 10, f"Report: {self.section_title}", 0, 1, 'C')
        self.ln(5)
        self.line(10, 32, 200, 32)

def generate_pdf(title, data_list):
    pdf = SchoolPDF()
    pdf.section_title = title
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    if data_list:
        df = pd.DataFrame(data_list)
        # Table Header
        pdf.set_fill_color(200, 220, 255)
        pdf.set_font("Arial", 'B', 10)
        col_width = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(col_width, 10, col, 1, 0, 'C', fill=True)
        pdf.ln()
        
        # Table Body
        pdf.set_font("Arial", '', 10)
        for _, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, 10, str(item), 1)
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGIN & SETUP ---
if not st.session_state.authenticated:
    st.title("🔐 System Activation")
    if date.today() > EXPIRY_DATE:
        st.error("License Expired.")
    else:
        key_input = st.text_input("Enter Activation Key", type="password")
        if st.button("Activate"):
            if key_input == ACTIVATION_KEY:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect Key.")

elif not st.session_state.school_setup_done:
    st.title("🏫 Institution Setup")
    s_name = st.text_input("Enter School Name")
    if st.button("Proceed"):
        if s_name:
            st.session_state.school_name = s_name
            st.session_state.school_setup_done = True
            st.rerun()

# --- 4. MAIN APP ---
else:
    st.sidebar.title(f"🏢 {st.session_state.school_name}")
    menu = st.sidebar.radio("Navigation", ["Section A: Student Load", "Section B: Teacher Profile", "Section C: Efficiency", "Section D: Feedback"])
    
    if st.sidebar.button("🚪 Logout / Reset"):
        st.session_state.authenticated = False
        st.session_state.school_setup_done = False
        st.rerun()

    data_key = menu.split(":")[0]
    st.title(menu)

    # --- DYNAMIC FORMS ---
    with st.form("entry_form", clear_on_submit=True):
        st.subheader("Add New Record")
        if data_key == "Section A":
            grade = st.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
            sec_name = st.text_input("Class Section (e.g., A, B, Blue, Green)") # User can type anything
            count = st.number_input("Total Students", min_value=1)
            needs = st.number_input("Special Needs", min_value=0)
            entry = {"Grade": grade, "Section": sec_name, "Students": count, "Special Needs": needs}
            
        elif data_key == "Section B":
            name = st.text_input("Teacher Name")
            qual = st.selectbox("Qualification", ["Bachelors", "Masters", "PhD"])
            exp = st.slider("Experience (Years)", 0, 40)
            entry = {"Name": name, "Qualification": qual, "Experience": exp}

        # (Other sections logic remains same...)
        elif data_key == "Section C":
            ratio = st.number_input("Target Ratio", min_value=1)
            admin = st.number_input("Admin Hours", min_value=0)
            entry = {"Ratio": ratio, "Admin Hours": admin}
        
        else: # Section D
            sat = st.slider("Satisfaction", 1, 10)
            peer = st.slider("Peer Score", 1, 10)
            entry = {"Satisfaction": sat, "Peer Score": peer}

        if st.form_submit_button("Submit Entry"):
            st.session_state.data_store[data_key].append(entry)
            st.rerun()

    # --- VIEW & DELETE ---
    current_list = st.session_state.data_store[data_key]
    if current_list:
        df_display = pd.DataFrame(current_list)
        st.dataframe(df_display, use_container_width=True)
        
        idx_to_del = st.number_input("Row index to delete", 0, len(current_list)-1, 0)
        if st.button("Delete Row"):
            st.session_state.data_store[data_key].pop(idx_to_del)
            st.rerun()

        if st.button("📥 Download PDF"):
            pdf_bytes = generate_pdf(menu, current_list)
            st.download_button("Click to Download", pdf_bytes, f"{data_key}.pdf")
