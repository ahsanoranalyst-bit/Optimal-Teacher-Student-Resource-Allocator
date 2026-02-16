

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
        "A": [], "B": [], "C": [], "Billing": [],
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
        school_name = st.session_state.data_store.get("School_Name", "GLOBAL ACADEMY").upper()
        self.cell(0, 12, school_name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "OFFICIAL FACULTY & BILLING REPORT", 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-20)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f"Page {self.page_no()} | Generated on: {datetime.now().strftime('%Y-%m-%d')}", 0, 0, 'C')

def generate_pdf_bytes(df, title):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"SECTION: {title}", 0, 1, 'L')
    pdf.ln(5)
    
    # Table Header
    pdf.set_font('Arial', 'B', 8)
    cols = df.columns
    col_width = 190 / len(cols)
    for col in cols:
        pdf.cell(col_width, 10, str(col), 1, 0, 'C')
    pdf.ln()
    
    # Table Body
    pdf.set_font('Arial', '', 8)
    for _, row in df.iterrows():
        for col in cols:
            pdf.cell(col_width, 9, str(row[col]), 1, 0, 'C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 2. AUTHENTICATION ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    key_input = st.text_input("Enter System Key", type="password")
    if st.button("Authenticate"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Invalid Key")

elif not st.session_state.setup_complete:
    st.title("⚙️ Institution Setup")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "Global International Academy")
    if st.button("🚀 Enter Dashboard"):
        st.session_state.setup_complete = True
        st.rerun()

# --- 3. MAIN DASHBOARD ---
else:
    st.sidebar.title(f"🏫 {st.session_state.data_store['School_Name']}")
    nav = st.sidebar.selectbox("Main Menu", ["Faculty Analysis", "Billing & Eid-ul-Fitr", "Student Records"])

    # --- FACULTY ANALYSIS (Best vs Improvement) ---
    if nav == "Faculty Analysis":
        st.header("👨‍🏫 Faculty Performance Categorization")
        
        # Adding Teacher Data
        with st.expander("➕ Add Teacher Record"):
            with st.form("teacher_form"):
                t_name = st.text_input("Teacher Name")
                t_sub = st.text_input("Subject")
                t_score = st.slider("Success Rate (%)", 0, 100, 75)
                if st.form_submit_button("Register Teacher"):
                    st.session_state.data_store["B"].append({"Name": t_name, "Subject": t_sub, "Score": t_score})
                    st.success("Teacher Registered!")

        if st.session_state.data_store["B"]:
            df_teachers = pd.DataFrame(st.session_state.data_store["B"])
            
            # Logic: Best (Score >= 80), Improvement (Score < 80)
            best_teachers = df_teachers[df_teachers['Score'] >= 80]
            imp_teachers = df_teachers[df_teachers['Score'] < 80]

            st.subheader("🌟 Best Teachers (Top Performers)")
            st.dataframe(best_teachers, use_container_width=True)
            if not best_teachers.empty:
                pdf_best = generate_pdf_bytes(best_teachers, "Best Teachers List")
                st.download_button("📥 Download Best Teachers PDF", pdf_best, "Best_Teachers.pdf")

            st.divider()

            st.subheader("📉 Improvement Required (Support Needed)")
            st.dataframe(imp_teachers, use_container_width=True)
            if not imp_teachers.empty:
                pdf_imp = generate_pdf_bytes(imp_teachers, "Improvement List")
                st.download_button("📥 Download Improvement List PDF", pdf_imp, "Improvement_Teachers.pdf")

    # --- BILLING & EID-UL-FITR ---
    elif nav == "Billing & Eid-ul-Fitr":
        st.header("💰 Billing Report & Eid-ul-Fitr Bonus")
        
        with st.form("billing_form"):
            b_name = st.text_input("Name (Staff/Teacher)")
            b_salary = st.number_input("Basic Salary", min_value=0)
            eid_bonus = st.number_input("Eid-ul-Fitr Bonus", min_value=0)
            if st.form_submit_button("Add to Billing"):
                total = b_salary + eid_bonus
                st.session_state.data_store["Billing"].append({
                    "Name": b_name, 
                    "Base Salary": b_salary, 
                    "Eid-ul-Fitr Bonus": eid_bonus,
                    "Total Payable": total,
                    "Date": datetime.now().strftime("%Y-%m-%d")
                })
                st.success("Billing Record Added!")

        if st.session_state.data_store["Billing"]:
            df_bill = pd.DataFrame(st.session_state.data_store["Billing"])
            st.dataframe(df_bill, use_container_width=True)
            pdf_bill = generate_pdf_bytes(df_bill, "Billing & Eid-ul-Fitr Report")
            st.download_button("📥 Download Billing Report PDF", pdf_bill, "Billing_Report.pdf")

    # --- STUDENT RECORDS (Maintaining Predictive Score) ---
    elif nav == "Student Records":
        st.header("📊 Student Performance & 5th Point Predictive Score")
        # Existing logic for student performance here...
        if st.session_state.data_store["A"]:
            df_students = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_students, use_container_width=True)
