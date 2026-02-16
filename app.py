

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io

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

# --- PROFESSIONAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        school_name = st.session_state.data_store.get("School_Name", "GLOBAL").upper()
        self.cell(0, 12, school_name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "ACADEMIC PERFORMANCE & DEPLOYMENT REPORT", 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-30)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "__________________________", 0, 1, 'R')
        self.cell(0, 5, "Authorized Signature", 0, 1, 'R')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.cell(0, 10, f"Date: {timestamp} | Page {self.page_no()}", 0, 0, 'L')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"SECTION: {title.upper()}", 0, 1, 'L')
    pdf.ln(5)
    if not df.empty:
        pdf.set_font('Arial', 'B', 8)
        w = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(w, 10, str(col), 1, 0, 'C')
        pdf.ln()
        pdf.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            for col in df.columns:
                pdf.cell(w, 9, str(row[col]), 1, 0, 'C')
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI DASHBOARD ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    key = st.text_input("Enter System Key", type="password")
    if st.button("Authenticate"):
        if key == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    # SECTION A: PERFORMANCE
    if nav == "Student Performance (A)":
        st.header("📊 Student Performance Records")
        with st.expander("➕ Manual Entry"):
            c1, c2 = st.columns(2)
            cls = c1.text_input("Class (e.g. Grade-1A)")
            sub = c2.text_input("Subject")
            g1, g2, g3, g4 = st.columns(4)
            a = g1.number_input("A", 0)
            b = g2.number_input("B", 0)
            c = g3.number_input("C", 0)
            d = g4.number_input("D", 0)
            if st.button("Save Entry"):
                score = calculate_predictive_score(a, b, c, d)
                st.session_state.data_store["A"].append({"Class": cls, "Subject": sub, "A": a, "B": b, "C": c, "D": d, "Predictive Score": score})
                st.rerun()
        
        display_key = "A"

    # SECTION B: TEACHERS
    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Teacher Experts Data")
        with st.expander("➕ Manual Entry"):
            t_name = st.text_input("Teacher Name")
            t_exp = st.text_input("Expertise (Subject)")
            t_succ = st.slider("Success Rate %", 0, 100, 80)
            if st.button("Add Teacher"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_succ})
                st.rerun()
        
        display_key = "B"

    # SECTION C: MAPPING
    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Strategic Deployment & Audit")
        results = []
        for p in st.session_state.data_store["A"]:
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == p['Subject']]
            best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0] if matches else None
            results.append({
                "Class": p['Class'], "Subject": p['Subject'], "Score": f"{p['Predictive Score']}%",
                "Assigned Teacher": best_t['Name'] if best_t else "HIRING REQUIRED",
                "Status": "❌ REPLACED" if p['Predictive Score'] < 50 else "✅ STABLE",
                "Audit": "Poor Performance" if p['Predictive Score'] < 50 else "Good"
            })
        st.session_state.data_store["C"] = results
        display_key = "C"

    # --- RENDER DATA, DELETE OPTION, & EXPORTS ---
    if st.session_state.data_store[display_key]:
        df_view = pd.DataFrame(st.session_state.data_store[display_key])
        st.dataframe(df_view, use_container_width=True)
        
        # DELETE ROW
        row_to_del = st.selectbox("Select row to delete", df_view.index)
        if st.button("🗑️ Delete Selected"):
            st.session_state.data_store[display_key].pop(row_to_del)
            st.rerun()

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            pdf_b = create_pdf(st.session_state.data_store[display_key], nav)
            st.download_button(f"📥 Download {nav} PDF", pdf_b, f"{nav}_Report.pdf")
        with col2:
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
                df_view.to_excel(writer, index=False)
            st.download_button(f"📊 Export {nav} Excel", out.getvalue(), f"{nav}_Data.xlsx")
