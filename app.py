

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. CORE INITIALIZATION ---
ACTIVATION_KEY = "PAK-2026"

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "A": [], "B": [], "School_Name": "Global International Academy"
    }

def calculate_predictive_score(a, b, c, d):
    total = a + b + c + d
    return round(((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total, 2) if total > 0 else 0

# --- 2. FIXED PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.data_store["School_Name"].upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, "TEACHER SHUFFLING & PERFORMANCE REPORT", 0, 1, 'C')
        self.ln(15)

def create_pdf(df, title):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    # Header
    col_width = 190 / len(df.columns)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), 1, 0, 'C')
    pdf.ln()
    # Data
    pdf.set_font('Arial', '', 9)
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, 10, str(val), 1, 0, 'C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MAIN INTERFACE ---
if not st.session_state.authenticated:
    st.title("🔐 Login")
    if st.text_input("Key", type="password") == ACTIVATION_KEY:
        if st.button("Access"): st.session_state.authenticated = True; st.rerun()
else:
    nav = st.sidebar.selectbox("Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    if nav == "Student Performance (A)":
        st.header("📊 Performance & Manual Entry")
        with st.form("a_form"):
            c1, c2 = st.columns(2)
            cls, sub = c1.text_input("Class"), c2.text_input("Subject")
            t_name = st.text_input("Current Teacher Name (Responsible for Result)")
            g1, g2, g3, g4 = st.columns(4)
            a, b, c, d = g1.number_input("A"), g2.number_input("B"), g3.number_input("C"), g4.number_input("D")
            if st.form_submit_button("Save Record"):
                st.session_state.data_store["A"].append({"Class": cls, "Subject": sub, "Current_Teacher": t_name, "Score": calculate_predictive_score(a,b,c,d)})
                st.rerun()

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Shuffling & Improvement Audit")
        results = []
        for p in st.session_state.data_store["A"]:
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == p['Subject']]
            best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0] if matches else None
            
            is_low = p['Score'] < 50
            results.append({
                "Class": p['Class'], "Subject": p['Subject'], "Result": f"{p['Score']}%",
                "Removed Teacher": p['Current_Teacher'] if is_low else "None",
                "New Expert": best_t['Name'] if (is_low and best_t) else p['Current_Teacher'],
                "Instruction": "SEND TO TRAINING" if is_low else "STABLE"
            })
        
        if results:
            df_res = pd.DataFrame(results)
            st.table(df_res)
            
            # PDF & EXCEL
            pdf_b = create_pdf(df_res, "Deployment")
            st.download_button("📥 Download PDF Report", pdf_b, "Report.pdf")
            
            out = io.BytesIO()
            df_res.to_excel(out, index=False)
            st.download_button("📊 Export Excel for Scheduling", out.getvalue(), "Shuffle_Data.xlsx")

    # Delete Functionality
    if st.sidebar.button("🗑️ Clear Last Record"):
        if st.session_state.data_store["A"]: st.session_state.data_store["A"].pop(); st.rerun()
