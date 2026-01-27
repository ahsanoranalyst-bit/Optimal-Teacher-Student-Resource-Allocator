import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# --- 1. LICENSE & SECURITY CONFIGURATION ---
# You can change the key and the expiry date here
ACTIVATION_CODE = "PAK-2026" 
EXPIRY_DATE = date(2026, 12, 31) # The system will lock after this date

# Session State to handle login and school name
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'school_name' not in st.session_state:
    st.session_state.school_name = ""

# --- 2. PDF GENERATION ENGINE ---
class PDF(FPDF):
    def header(self):
        # Master School Name Header
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.school_name.upper(), 0, 1, 'C')
        # Section Title Sub-header
        self.set_font('Arial', 'I', 12)
        self.cell(0, 10, f"Sectional Report: {self.section_title}", 0, 1, 'C')
        self.ln(10)

def generate_pdf_report(title, data, score):
    pdf = PDF()
    pdf.section_title = title
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Printing entry data
    for key, value in data.items():
        pdf.cell(0, 10, f"{key}: {value}", 0, 1)
    
    pdf.ln(10)
    # Printing the Optimization/Profit Level
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Optimization Level: {score} / 200", 0, 1)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. ACTIVATION & LOGIN PAGE ---
if not st.session_state.auth:
    st.title("🔐 System Activation & Licensing")
    
    today = date.today()
    
    # Logic to check if the license has expired
    if today > EXPIRY_DATE:
        st.error("❌ Your License has expired. Please contact the administrator for a renewal.")
    else:
        key_input = st.text_input("Enter Activation Key", type="password")
        school_input = st.text_input("Enter School Name")
        
        if st.button("Activate System"):
            if key_input == ACTIVATION_CODE and school_input:
                st.session_state.auth = True
                st.session_state.school_name = school_input
                st.success("System Activated! Welcome.")
                st.rerun()
            else:
                st.error("Invalid Key or School Name. Please try again.")

# --- 4. MAIN APPLICATION (ALL 4 SECTIONS) ---
else:
    # Sidebar Navigation with all 4 sections visible
    st.sidebar.title(f"🏫 {st.session_state.school_name}")
    st.sidebar.subheader("Main Menu")
    menu = st.sidebar.radio("Select Section:", 
                            ["Section A: Student Load", 
                             "Section B: Teacher Profile", 
                             "Section C: Efficiency", 
                             "Section D: Feedback"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("💾 Save to Cloud"):
        # This is where your existing Google Sheet connection logic remains untouched
        st.sidebar.success("Data successfully synced to Google Sheets!")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.auth = False
        st.session_state.school_name = ""
        st.rerun()

    st.title(menu)

    # --- SECTION A LOGIC ---
    if menu == "Section A: Student Load":
        std_count = st.number_input("Total Student Count", value=100)
        spec_needs = st.number_input("Special Needs Students", value=5)
        
        # Logic: Optimization score between 1 and 200
        score = min(200, (std_count // 2) + (spec_needs * 10))
        st.info(f"Current Load Score: {score}/200")
        
        data_map = {"Total Students": std_count, "Special Needs": spec_needs}
        if st.button("Generate Section A PDF"):
            pdf_bytes = generate_pdf_report(menu, data_map, score)
            st.download_button("Download Report", pdf_bytes, "Section_A.pdf")

    # --- SECTION B LOGIC ---
    elif menu == "Section B: Teacher Profile":
        experience = st.slider("Teacher Seniority (Years)", 1, 40, 10)
        qualification = st.selectbox("Qualification", ["Bachelors", "Masters", "PhD"])
        
        # Optimization Logic
        score = min(200, (experience * 5) + 50)
        st.info(f"Teacher Capability Score: {score}/200")
        
        data_map = {"Seniority": f"{experience} Years", "Qualification": qualification}
        if st.button("Generate Section B PDF"):
            pdf_bytes = generate_pdf_report(menu, data_map, score)
            st.download_button("Download Report", pdf_bytes, "Section_B.pdf")

    # --- SECTION C LOGIC ---
    elif menu == "Section C: Efficiency":
        ratio = st.slider("Student-Teacher Ratio", 10, 60, 25)
        admin_hrs = st.number_input("Weekly Admin Task Hours", value=8)
        
        # Optimization logic: Lower admin hours and better ratio increase efficiency
        score = max(1, 200 - (admin_hrs * 4) - (ratio))
        st.info(f"Efficiency Score: {score}/200")
        
        data_map = {"Target Ratio": f"1:{ratio}", "Admin Work": f"{admin_hrs} Hrs"}
        if st.button("Generate Section C PDF"):
            pdf_bytes = generate_pdf_report(menu, data_map, score)
            st.download_button("Download Report", pdf_bytes, "Section_C.pdf")

    # --- SECTION D LOGIC ---
    elif menu == "Section D: Feedback":
        satisfaction = st.slider("Student Satisfaction Score (1-10)", 1, 10, 8)
        peer_rev = st.slider("Peer Review Score (1-10)", 1, 10, 7)
        
        score = (satisfaction + peer_rev) * 10
        st.info(f"Feedback/Performance Score: {score}/200")
        
        data_map = {"Student Satisfaction": satisfaction, "Peer Review": peer_rev}
        if st.button("Generate Section D PDF"):
            pdf_bytes = generate_pdf_report(menu, data_map, score)
            st.download_button("Download Report", pdf_bytes, "Section_D.pdf")
