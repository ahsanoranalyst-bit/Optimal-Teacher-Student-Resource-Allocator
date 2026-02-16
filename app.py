

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
        self.set_font('Arial', 'B', 16)
        name = st.session_state.data_store.get("School_Name", "ACADEMY").upper()
        self.cell(0, 12, name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "OFFICIAL PERFORMANCE REPORT", 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(20)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, "Authorized Signature: __________________________", 0, 1, 'R')
        ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.cell(0, 10, f"Date: {ts} | Page {self.page_no()}", 0, 0, 'L')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"REPORT TYPE: {title.upper()}", 0, 1, 'L')
    pdf.ln(5)
    
    if not df.empty:
        col_count = len(df.columns)
        w = 190 / col_count 
        
        pdf.set_font('Arial', 'B', 8)
        pdf.set_fill_color(230, 230, 230)
        for col in df.columns:
            pdf.cell(w, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 7)
        for _, row in df.iterrows():
            for col in df.columns:
                pdf.cell(w, 8, str(row[col]), 1, 0, 'C')
            pdf.ln()
            
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI & NAVIGATION ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    pwd = st.text_input("Enter Activation Key", type="password")
    if st.button("Login"):
        if pwd == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    st.title("⚙️ Institution Setup")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "Global International Academy")
    if st.button("🚀 Enter Dashboard"):
        st.session_state.setup_complete = True
        st.rerun()

else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)", "Teacher Portal"])

    # --- SECTION C: EFFICIENCY MAPPING ---
    if nav == "Efficiency Mapping (C)":
        st.header("🎯 Efficiency Mapping & Separate Reports")
        
        if st.button("🔄 Auto-Map All Teachers"):
            st.session_state.data_store["C"] = []
            for teacher in st.session_state.data_store["B"]:
                relevant_data = [a for a in st.session_state.data_store["A"] if a['Subject'].lower() == teacher['Expertise'].lower()]
                
                if relevant_data:
                    for record in relevant_data:
                        status = "BEST TEACHER" if record['Predictive Score'] >= 70 else "IMPROVEMENT NEEDED"
                        st.session_state.data_store["C"].append({
                            "Class": record['Class'], 
                            "Subject": teacher['Expertise'], 
                            "Teacher": teacher['Name'], 
                            "Predictive Score": record['Predictive Score'],
                            "Status": status
                        })
                else:
                    st.session_state.data_store["C"].append({
                        "Class": "N/A", "Subject": teacher['Expertise'], "Teacher": teacher['Name'], 
                        "Predictive Score": 0, "Status": "NO DATA FOUND"
                    })
            st.success("Mapping Completed!")

        if st.session_state.data_store["C"]:
            df_full = pd.DataFrame(st.session_state.data_store["C"])
            st.subheader("Current Mapping Overview")
            st.dataframe(df_full)
            
            # --- SEPARATE PDF GENERATION ---
            best_teachers_df = df_full[df_full["Status"] == "BEST TEACHER"]
            improvement_needed_df = df_full[df_full["Status"].isin(["IMPROVEMENT NEEDED", "NO DATA FOUND"])]
            
            st.markdown("---")
            st.subheader("📥 Download Separate Reports")
            col1, col2 = st.columns(2)
            
            with col1:
                if not best_teachers_df.empty:
                    st.success(f"Found {len(best_teachers_df)} Best Performers")
                    st.download_button(
                        label="📥 Download Best Teachers PDF",
                        data=create_pdf(best_teachers_df, "Best Teachers List"),
                        file_name="Best_Teachers_Report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.info("No 'Best Teacher' records found.")

            with col2:
                if not improvement_needed_df.empty:
                    st.warning(f"Found {len(improvement_needed_df)} Records for Improvement")
                    st.download_button(
                        label="📥 Download Improvement List PDF",
                        data=create_pdf(improvement_needed_df, "Improvement Needed List"),
                        file_name="Improvement_Needed_Report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.info("No records needing improvement found.")

    # --- TEACHER PORTAL ---
    elif nav == "Teacher Portal":
        st.header("📜 Teacher Personal Portal")
        if st.session_state.data_store["B"]:
            names = [t['Name'] for t in st.session_state.data_store["B"]]
            selected = st.selectbox("Select Teacher", names)
            report_data = [x for x in st.session_state.data_store["C"] if x['Teacher'] == selected]
            
            if report_data:
                st.dataframe(pd.DataFrame(report_data))
                st.download_button(f"📥 Download {selected}'s Individual PDF", create_pdf(report_data, f"Individual Report: {selected}"), f"{selected}_Report.pdf")
            else:
                st.info("No data found for this teacher. Please run Auto-Map first.")

    # Remaining sections (A and B) can be added similarly.
