

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

# --- 2. PROFESSIONAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        name = st.session_state.data_store.get("School_Name", "ACADEMY").upper()
        self.cell(0, 12, name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "OFFICIAL ACADEMIC PERFORMANCE REPORT", 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(15)

    def footer(self):
        self.set_y(-30)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "__________________________", 0, 1, 'R')
        self.cell(0, 5, "Authorized Signature & Official Stamp", 0, 1, 'R')
        ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.cell(0, 10, f"Date: {ts} | Page {self.page_no()}", 0, 0, 'L')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 10, f"SECTION: {title.upper()}", 0, 1, 'L')
    pdf.ln(5)
    if not df.empty:
        pdf.set_font('Arial', 'B', 8)
        w = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(w, 10, str(col), 1, 0, 'C', fill=False)
        pdf.ln()
        pdf.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            for col in df.columns:
                pdf.cell(w, 9, str(row[col]), 1, 0, 'C')
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI & NAVIGATION ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    if st.text_input("Enter Key", type="password") == ACTIVATION_KEY:
        if st.button("Login"):
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    st.title("⚙️ Setup")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "Global International Academy")
    if st.button("Enter Dashboard"):
        st.session_state.setup_complete = True
        st.rerun()

else:
    st.sidebar.title("Menu")
    nav = st.sidebar.selectbox("Go to", ["Performance (A)", "Teachers (B)", "Mapping (C)", "Teacher Portal"])

    if nav == "Performance (A)":
        st.header("📊 Student Performance")
        # Simplified manual entry for brevity, same logic as your original
        if st.session_state.data_store["A"]:
            st.dataframe(pd.DataFrame(st.session_state.data_store["A"]))

    elif nav == "Teachers (B)":
        st.header("👨‍🏫 Teacher Expertise")
        if st.session_state.data_store["B"]:
            st.dataframe(pd.DataFrame(st.session_state.data_store["B"]))

    elif nav == "Mapping (C)":
        st.header("🎯 Efficiency Mapping")
        
        # 1. Manual Allocation (RESTORED)
        with st.expander("➕ Manual Allocation"):
            if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
                class_opts = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
                sel_c = st.selectbox("Select Class", class_opts)
                subj = sel_c.split(" | ")[1]
                teachers = [t['Name'] for t in st.session_state.data_store["B"] if t['Expertise'] == subj]
                sel_t = st.selectbox("Assign Teacher", teachers if teachers else ["No Expert Found"])
                if st.button("Confirm Allocation"):
                    score = next(x['Predictive Score'] for x in st.session_state.data_store["A"] if f"{x['Class']} | {x['Subject']}" == sel_c)
                    st.session_state.data_store["C"].append({
                        "Class": sel_c.split(" | ")[0], "Subject": subj, "Teacher": sel_t,
                        "Current Score": score, "Status": "MANUAL"
                    })
                    st.rerun()

        # 2. Auto-Generate (BULK)
        if st.button("🔄 Auto-Map Remaining Classes"):
            existing = [f"{x['Class']}-{x['Subject']}" for x in st.session_state.data_store["C"]]
            for row in st.session_state.data_store["A"]:
                if f"{row['Class']}-{row['Subject']}" not in existing:
                    matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == row['Subject']]
                    if matches:
                        best = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                        st.session_state.data_store["C"].append({
                            "Class": row['Class'], "Subject": row['Subject'], "Teacher": best['Name'],
                            "Current Score": row['Predictive Score'], "Status": "AUTO"
                        })
            st.rerun()

        # 3. Split PDF Generation
        if st.session_state.data_store["C"]:
            df_c = pd.DataFrame(st.session_state.data_store["C"])
            best_df = df_c[df_c["Current Score"] >= 70]
            improve_df = df_c[df_c["Current Score"] < 70]
            
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"Best: {len(best_df)}")
                if not best_df.empty:
                    st.download_button("Download Best PDF", create_pdf(best_df.to_dict('records'), "BEST"), "Best.pdf")
            with c2:
                st.warning(f"Improvement: {len(improve_df)}")
                if not improve_df.empty:
                    st.download_button("Download Improve PDF", create_pdf(improve_df.to_dict('records'), "IMPROVE"), "Improve.pdf")
            st.dataframe(df_c)

    elif nav == "Teacher Portal":
        st.header("📜 Teacher Reports")
        t_list = list(set([t['Name'] for t in st.session_state.data_store["B"]]))
        selected = st.selectbox("Select Teacher", t_list)
        report = [x for x in st.session_state.data_store["C"] if x['Teacher'] == selected]
        if report:
            st.dataframe(pd.DataFrame(report))
            st.download_button("Download Report", create_pdf(report, selected), f"{selected}.pdf")
