

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. CORE INITIALIZATION ---
ACTIVATION_KEY = "PAK-2026"

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Grades_Config": {},
        "A": [], "B": [], "C": [],
        "School_Name": "Global International Academy"
    }

# --- PREDICTIVE ENGINE ---
def calculate_predictive_score(a, b, c, d):
    total = a + b + c + d
    if total == 0: return 0
    score = ((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total
    return round(score, 2)

# --- 2. PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        school_name = st.session_state.data_store.get("School_Name", "GLOBAL").upper()
        self.cell(0, 12, school_name, 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, 'C')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"SECTION: {title.upper()}", 0, 1, 'L')
    pdf.ln(5)
    
    if not df.empty:
        pdf.set_font('Arial', 'B', 8)
        for col in df.columns:
            pdf.cell(35, 10, str(col), 1, 0, 'C')
        pdf.ln()
        pdf.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            for col in df.columns:
                pdf.cell(35, 9, str(row[col]), 1, 0, 'C')
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. BULK UPLOAD & MULTI-VIEW LOGIC ---
def handle_bulk_upload():
    st.sidebar.markdown("### 📂 Bulk Import")
    uploaded_files = st.sidebar.file_uploader("Upload all Excel files", type=["xlsx"], accept_multiple_files=True)

    if uploaded_files and st.sidebar.button("Process All"):
        for file in uploaded_files:
            df = pd.read_excel(file).fillna('')
            name = file.name.lower()
            if "class" in name:
                for _, row in df.iterrows():
                    key = f"{row['Grade']}-{row['Section']}"
                    st.session_state.data_store["Grades_Config"][key] = [s.strip() for s in str(row['Subjects']).split(",")]
            elif "student" in name:
                for _, row in df.iterrows():
                    p_score = calculate_predictive_score(int(row['A']), int(row['B']), int(row['C']), int(row['D']))
                    st.session_state.data_store["A"].append({
                        "Class": row['Class'], "Subject": row['Subject'],
                        "A": row['A'], "B": row['B'], "C": row['C'], "D": row['D'],
                        "Predictive Score": p_score
                    })
            elif "teacher" in name:
                for _, row in df.iterrows():
                    st.session_state.data_store["B"].append({"Name": row['Name'], "Expertise": row['Expertise'], "Success": row['Success']})
        st.sidebar.success("All data imported!")
        st.rerun()

    # Dashboard Tabs for side-by-side viewing
    if st.session_state.data_store["Grades_Config"] or st.session_state.data_store["A"]:
        st.subheader("Data Overview")
        tab1, tab2, tab3 = st.tabs(["Classes", "Students", "Teachers"])
        with tab1: st.write(st.session_state.data_store["Grades_Config"])
        with tab2: st.dataframe(st.session_state.data_store["A"])
        with tab3: st.dataframe(st.session_state.data_store["B"])

# --- 4. MAIN INTERFACE ---
if not st.session_state.authenticated:
    st.title("🔐 Login")
    if st.text_input("System Key", type="password") == ACTIVATION_KEY:
        if st.button("Access"): 
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    handle_bulk_upload()
    st.title("⚙️ Setup")
    if st.button("Complete Setup"):
        st.session_state.setup_complete = True
        st.rerun()

else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    if nav == "Efficiency Mapping (C)":
        st.header("🎯 Strategic Deployment")
        # Logic for Driver scheduling (Far to Near) can be visualized here
        st.info("Note: Pickup starts from furthest location; Drop-off starts from nearest.")
        if st.session_state.data_store["C"]:
            st.table(st.session_state.data_store["C"])
            
    # Add PDF Download buttons for current view
    target = "A" if "Student" in nav else "B" if "Teacher" in nav else "C"
    if st.session_state.data_store[target]:
        pdf_file = create_pdf(st.session_state.data_store[target], nav)
        st.download_button(f"Download {nav} PDF", pdf_file, "Report.pdf")
