

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. INITIALIZATION ---
ACTIVATION_KEY = "PAK-2026"

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "A": [], # Student Performance
        "B": [], # Teacher Experts
        "School_Name": "Global International Academy"
    }

def calculate_predictive_score(a, b, c, d):
    total = a + b + c + d
    return round(((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total, 2) if total > 0 else 0

# --- 2. PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.data_store["School_Name"].upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, "OFFICIAL ACADEMIC & DEPLOYMENT REPORT", 0, 1, 'C')
        self.ln(15)

def create_pdf(df, title):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    col_width = 190 / len(df.columns)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), 1, 0, 'C')
    pdf.ln()
    pdf.set_font('Arial', '', 9)
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, 10, str(val), 1, 0, 'C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MAIN APP ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    key_input = st.text_input("Enter Key", type="password")
    if st.button("Login"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    
    # Sidebar for Bulk Import
    st.sidebar.header("📂 Bulk Import")
    up_type = st.sidebar.selectbox("Category", ["Student Performance", "Teachers"])
    up_file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])
    if up_file and st.sidebar.button("Confirm Import"):
        df = pd.read_excel(up_file).fillna('')
        if up_type == "Student Performance":
            for _, r in df.iterrows():
                score = calculate_predictive_score(int(r['A']), int(r['B']), int(r['C']), int(r['D']))
                st.session_state.data_store["A"].append({"Class": r['Class'], "Subject": r['Subject'], "Teacher": r['Teacher'], "Score": score})
        else:
            for _, r in df.iterrows():
                st.session_state.data_store["B"].append({"Name": r['Name'], "Expertise": r['Expertise'], "Success": r['Success']})
        st.success("Imported!")

    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    # Section A: Performance
    if nav == "Student Performance (A)":
        st.header("📊 Student Performance & Manual Entry")
        with st.form("manual_a"):
            c1, c2, c3 = st.columns(3)
            cls, sub, t_name = c1.text_input("Class"), c2.text_input("Subject"), c3.text_input("Current Teacher")
            g1, g2, g3, g4 = st.columns(4)
            a, b, c, d = g1.number_input("A", 0), g2.number_input("B", 0), g3.number_input("C", 0), g4.number_input("D", 0)
            if st.form_submit_button("Save Entry"):
                st.session_state.data_store["A"].append({"Class": cls, "Subject": sub, "Teacher": t_name, "Score": calculate_predictive_score(a,b,c,d)})
                st.rerun()
        
        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_a)
            idx = st.selectbox("Select Row to Delete", df_a.index)
            if st.button("🗑️ Delete Record"):
                st.session_state.data_store["A"].pop(idx)
                st.rerun()

    # Section B: Teachers
    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Teacher Registry")
        with st.form("manual_b"):
            n, e, s = st.text_input("Name"), st.text_input("Expertise"), st.slider("Success Rate", 0, 100)
            if st.form_submit_button("Add Teacher"):
                st.session_state.data_store["B"].append({"Name": n, "Expertise": e, "Success": s})
                st.rerun()
        
        if st.session_state.data_store["B"]:
            df_b = pd.DataFrame(st.session_state.data_store["B"])
            st.dataframe(df_b)
            idx = st.selectbox("Delete Teacher Index", df_b.index)
            if st.button("🗑️ Remove Teacher"):
                st.session_state.data_store["B"].pop(idx)
                st.rerun()

    # Section C: Mapping & Shuffling
    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Deployment Audit & Shuffling")
        results = []
        for p in st.session_state.data_store["A"]:
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == p['Subject']]
            best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0] if matches else None
            
            is_low = p['Score'] < 50
            results.append({
                "Class": p['Class'], "Subject": p['Subject'], "Result": f"{p['Score']}%",
                "Original Teacher": p['Teacher'],
                "New Assigned": best_t['Name'] if (is_low and best_t) else p['Teacher'],
                "Instruction": "TRANSFER TO TRAINING" if is_low else "STABLE"
            })
        
        if results:
            df_c = pd.DataFrame(results)
            st.table(df_c)
            
            # PDF & Excel Downloads
            pdf_b = create_pdf(df_c, "Mapping")
            st.download_button("📥 Download Report (PDF)", pdf_b, "Deployment_Report.pdf")
            
            xl_io = io.BytesIO()
            df_c.to_excel(xl_io, index=False)
            st.download_button("📊 Export for Scheduling (Excel)", xl_io.getvalue(), "Shuffle_Data.xlsx")
