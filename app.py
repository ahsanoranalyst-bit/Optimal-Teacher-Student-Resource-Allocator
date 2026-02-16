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
    # Weightage: A=100%, B=75%, C=50%, D=25%
    score = ((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total
    return round(score, 2)

# --- 2. PROFESSIONAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        school_name = st.session_state.data_store.get("School_Name", "GLOBAL ACADEMY").upper()
        self.cell(0, 12, school_name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "OFFICIAL ADMINISTRATION & PERFORMANCE REPORT", 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.cell(0, 10, f"Report Generated: {timestamp} | Page {self.page_no()}", 0, 0, 'L')
        self.cell(0, 10, "Admin Signature: ________________", 0, 0, 'R')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 10, f"REPORT CATEGORY: {title.upper()}", 0, 1, 'L')
    pdf.ln(5)
    
    if not df.empty:
        # Columns arrangement: Predictive Score as 5th point
        col_order = ["Institution", "Class", "Subject", "Teacher", "Predictive Score", "Status"]
        df = df[col_order] if all(c in df.columns for c in col_order) else df
        
        column_widths = {"Institution": 40, "Class": 20, "Subject": 25, "Teacher": 35, "Predictive Score": 35, "Status": 35}
        
        pdf.set_font('Arial', 'B', 8)
        pdf.set_fill_color(230, 235, 245)
        for col in df.columns:
            pdf.cell(column_widths.get(col, 30), 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            for col in df.columns:
                pdf.cell(column_widths.get(col, 30), 9, str(row[col]), 1, 0, 'C')
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MAIN APPLICATION ---
if not st.session_state.authenticated:
    st.title("🔐 Admin Login")
    key = st.text_input("System Key", type="password")
    if st.button("Unlock System"):
        if key == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    st.title("⚙️ Initial Setup")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "Global International Academy")
    if st.button("Save & Open Dashboard"):
        st.session_state.setup_complete = True
        st.rerun()

else:
    st.sidebar.title("ADMIN PANEL")
    nav = st.sidebar.selectbox("Navigation", ["Students (A)", "Teachers (B)", "Mapping & Reports (C)"])

    if nav == "Students (A)":
        st.header("📊 Student Performance Entry")
        with st.form("manual_a"):
            c1, c2 = st.columns(2)
            cls = c1.text_input("Class/Grade")
            sub = c2.text_input("Subject")
            g1, g2, g3, g4 = st.columns(4)
            a = g1.number_input("A", 0)
            b = g2.number_input("B", 0)
            c = g3.number_input("C", 0)
            d = g4.number_input("D", 0)
            if st.form_submit_button("Save Record"):
                score = calculate_predictive_score(a, b, c, d)
                st.session_state.data_store["A"].append({"Class": cls, "Subject": sub, "Predictive Score": score})
                st.success("Record Saved")

    elif nav == "Teachers (B)":
        st.header("👨‍🏫 Faculty Registration")
        with st.form("manual_b"):
            name = st.text_input("Teacher Name")
            exp = st.text_input("Expertise (Subject)")
            rate = st.slider("Success Rate", 0, 100, 75)
            if st.form_submit_button("Register Teacher"):
                st.session_state.data_store["B"].append({"Name": name, "Expertise": exp, "Success": rate})
                st.success("Teacher Added")

    elif nav == "Mapping & Reports (C)":
        st.header("🎯 Efficiency Mapping & Admin Reports")
        
        # Mapping Logic
        if st.session_state.data_store["A"]:
            st.subheader("Assign & Categorize")
            for i, record in enumerate(st.session_state.data_store["A"]):
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{record['Class']}** - {record['Subject']} (Score: {record['Predictive Score']}%)")
                if col2.button(f"Map Record {i}"):
                    # Logic for Admin PDF separation
                    score = record['Predictive Score']
                    if score >= 75: status = "BEST TEACHER"
                    elif 45 <= score < 75: status = "PROMOTE TEACHER"
                    else: status = "IMPROVEMENT REQUIRED"
                    
                    st.session_state.data_store["C"].append({
                        "Institution": st.session_state.data_store["School_Name"],
                        "Class": record['Class'], "Subject": record['Subject'],
                        "Teacher": "Assigned Staff", "Predictive Score": score, "Status": status
                    })
                    st.rerun()

        # Admin Reports Section
        if st.session_state.data_store["C"]:
            st.divider()
            st.subheader("📁 Admin Master Reports")
            df_master = pd.DataFrame(st.session_state.data_store["C"])
            
            # Separate Lists
            best_list = df_master[df_master['Status'] == "BEST TEACHER"]
            promote_list = df_master[df_master['Status'] == "PROMOTE TEACHER"]
            improve_list = df_master[df_master['Status'] == "IMPROVEMENT REQUIRED"]

            # Display and Download Buttons
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.info("🌟 Best List")
                st.dataframe(best_list)
                if not best_list.empty:
                    st.download_button("Download Best PDF", create_pdf(best_list.to_dict('records'), "Best Teachers"), "Best_Report.pdf")

            with c2:
                st.warning("📈 Promote List")
                st.dataframe(promote_list)
                if not promote_list.empty:
                    st.download_button("Download Promote PDF", create_pdf(promote_list.to_dict('records'), "Promote List"), "Promote_Report.pdf")

            with c3:
                st.error("⚠️ Improve List")
                st.dataframe(improve_list)
                if not improve_list.empty:
                    st.download_button("Download Improve PDF", create_pdf(improve_list.to_dict('records'), "Improvement Required"), "Improvement_Report.pdf")

            if st.button("🗑️ Clear All Mapping Records"):
                st.session_state.data_store["C"] = []
                st.rerun()
