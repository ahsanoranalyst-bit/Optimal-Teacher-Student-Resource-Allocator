

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
    if total == 0: return 0
    # Formula: A=100%, B=75%, C=50%, D=25%
    return round(((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total, 2)

# --- 2. PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.data_store["School_Name"].upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, "OFFICIAL ACADEMIC AUDIT REPORT", 0, 1, 'C')
        self.ln(15)

def create_pdf(df, title):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Section: {title}", 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 8)
    col_width = 190 / len(df.columns)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), 1, 0, 'C')
    pdf.ln()
    pdf.set_font('Arial', '', 8)
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, 10, str(val), 1, 0, 'C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MAIN APP ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    if st.text_input("Enter Key", type="password") == ACTIVATION_KEY:
        if st.button("Login"): st.session_state.authenticated = True; st.rerun()
else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    
    # Sidebar Imports
    st.sidebar.header("📂 Bulk Import")
    up_type = st.sidebar.selectbox("Category", ["Student Performance", "Teachers"])
    up_file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])
    if up_file and st.sidebar.button("Confirm Import"):
        df_up = pd.read_excel(up_file).fillna(0)
        if up_type == "Student Performance":
            for _, r in df_up.iterrows():
                score = calculate_predictive_score(int(r['A']), int(r['B']), int(r['C']), int(r['D']))
                st.session_state.data_store["A"].append({
                    "Class": str(r['Class']), "Subject": str(r['Subject']), 
                    "Teacher": str(r.get('Teacher', 'N/A')), "Predictive_Score": score
                })
        else:
            for _, r in df_up.iterrows():
                st.session_state.data_store["B"].append({
                    "Name": str(r['Name']), "Expertise": str(r['Expertise']), "Success": int(r['Success'])
                })
        st.sidebar.success("Imported!")

    nav = st.sidebar.selectbox("Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    # --- SECTION A ---
    if nav == "Student Performance (A)":
        st.header("📊 Section A: Performance Data")
        with st.expander("➕ Manual Entry"):
            c1, c2, c3 = st.columns(3)
            m_cls, m_sub, m_t = c1.text_input("Class"), c2.text_input("Subject"), c3.text_input("Current Teacher")
            g1, g2, g3, g4 = st.columns(4)
            ma, mb, mc, md = g1.number_input("A",0), g2.number_input("B",0), g3.number_input("C",0), g4.number_input("D",0)
            if st.button("Save Entry"):
                st.session_state.data_store["A"].append({"Class": m_cls, "Subject": m_sub, "Teacher": m_t, "Predictive_Score": calculate_predictive_score(ma,mb,mc,md)})
                st.rerun()

        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_a)
            if st.button("🗑️ Delete Row"): st.session_state.data_store["A"].pop(); st.rerun()
            st.download_button("📥 Download A (PDF)", create_pdf(df_a, "Performance"), "Section_A.pdf")
            xl_a = io.BytesIO()
            df_a.to_excel(xl_a, index=False)
            st.download_button("📊 Export A (Excel)", xl_a.getvalue(), "Section_A.xlsx")

    # --- SECTION B ---
    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Section B: Teacher Experts")
        with st.expander("➕ Manual Teacher Entry"):
            tn, te, ts = st.text_input("Name"), st.text_input("Expertise"), st.slider("Success", 0, 100, 70)
            if st.button("Add Teacher"):
                st.session_state.data_store["B"].append({"Name": tn, "Expertise": te, "Success": ts})
                st.rerun()
        
        if st.session_state.data_store["B"]:
            df_b = pd.DataFrame(st.session_state.data_store["B"])
            st.dataframe(df_b)
            if st.button("🗑️ Delete Teacher"): st.session_state.data_store["B"].pop(); st.rerun()
            st.download_button("📥 Download B (PDF)", create_pdf(df_b, "Teachers"), "Section_B.pdf")

    # --- SECTION C: EFFICIENCY MAPPING (FIXED) ---
    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Section C: Shuffling & Audit")
        audit_list = []
        for p in st.session_state.data_store["A"]:
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == p['Subject']]
            best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0] if matches else None
            needs_shuffle = p['Predictive_Score'] < 50
            
            audit_list.append({
                "Class": p['Class'],
                "Subject": p['Subject'],
                "Original_Teacher": p['Teacher'],
                "Score": f"{p['Predictive_Score']}%",
                "Assigned_Teacher": best_t['Name'] if (needs_shuffle and best_t) else p['Teacher'],
                "Status": "❌ REPLACED" if needs_shuffle else "✅ STABLE",
                "Remark": "SEND TO TRAINING" if needs_shuffle else "EXCELLENT"
            })

        if audit_list:
            df_c = pd.DataFrame(audit_list)
            st.table(df_c)
            st.download_button("📥 Download Audit (PDF)", create_pdf(df_c, "Audit"), "Final_Audit.pdf")
            xl_c = io.BytesIO()
            df_c.to_excel(xl_c, index=False)
            st.download_button("📊 Export for Scheduling (Excel)", xl_c.getvalue(), "Shuffle_Final.xlsx")
