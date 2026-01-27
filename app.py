https://g.co/gemini/share/d522f89168c9 

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date
import io

# --- 1. SETTINGS & LICENSE ---
ACTIVATION_KEY = "PAK-2026"
EXPIRY_DATE = date(2026, 12, 31)

# Initialize Session States securely
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'school_setup_done' not in st.session_state:
    st.session_state.school_setup_done = False
if 'school_name' not in st.session_state:
    st.session_state.school_name = ""
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Section A": [], "Section B": [], "Section C": [], "Section D": []
    }

# --- 2. LOGICAL OPTIMIZATION ENGINE (1-200 Scale) ---
def calculate_optimization(section, data_list):
    if not data_list:
        return 0
    
    # Logic: More resources/better feedback = higher score towards 200
    if section == "Section A":
        # Higher student count with low special needs is efficient
        total_std = sum(item['Students'] for item in data_list)
        total_spec = sum(item['Special Needs'] for item in data_list)
        score = (total_std / 10) - (total_spec * 2)
    elif section == "Section B":
        # Experience and PhDs increase score
        score = sum(item['Experience'] for item in data_list) / len(data_list) * 5
    else:
        score = 100 # Base score for others
        
    return min(200, max(1, int(score + 50)))

# --- 3. PROFESSIONAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, st.session_state.school_name.upper(), 0, 1, 'C')
        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 10, f"DEPARTMENTAL ANALYSIS: {self.section_title}", 0, 1, 'C')
        self.ln(5)
        self.line(10, 35, 200, 35)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Report Date: {datetime.now().strftime("%Y-%m-%d")} | Confidential', 0, 0, 'C')

def generate_pdf(title, data_list, opt_score):
    pdf = SchoolPDF()
    pdf.section_title = title
    pdf.add_page()
    
    # Summary Box
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 12, f"Resource Optimization Score: {opt_score} / 200", 1, 1, 'C', fill=True)
    pdf.ln(10)
    
    if data_list:
        df = pd.DataFrame(data_list)
        # Table Header
        pdf.set_fill_color(52, 73, 94)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", 'B', 10)
        
        col_width = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        
        # Table Rows
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", '', 9)
        for _, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, 9, str(item), 1, 0, 'C')
            pdf.ln()
            
    return pdf.output(dest='S').encode('latin-1')

# --- 4. NAVIGATION & ACCESS CONTROL ---
if not st.session_state.authenticated:
    st.title("🔐 Enterprise Resource Portal")
    if date.today() > EXPIRY_DATE:
        st.error("System License Expired. Please renew your subscription.")
    else:
        with st.container():
            key = st.text_input("Activation Key", type="password", help="Enter the 8-digit license key")
            if st.button("Authenticate System", use_container_width=True):
                if key == ACTIVATION_KEY:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid Key")

elif not st.session_state.school_setup_done:
    st.title("🏫 Account Setup")
    school_name = st.text_input("Enter Registered Institution Name")
    if st.button("Initialize Dashboard"):
        if school_name:
            st.session_state.school_name = school_name
            st.session_state.school_setup_done = True
            st.rerun()

# --- 5. MAIN DASHBOARD ---
else:
    st.sidebar.title(f"🏢 {st.session_state.school_name}")
    st.sidebar.write(f"System Date: {date.today()}")
    
    menu = st.sidebar.selectbox("Navigate Department", 
        ["Section A: Student Load", "Section B: Teacher Profile", 
         "Section C: Efficiency", "Section D: Feedback"])
    
    if st.sidebar.button("🚪 Logout & Lock"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.title(menu)
    data_key = menu.split(":")[0]

    # --- DYNAMIC ENTRY FORM ---
    with st.expander("➕ Add New Entry", expanded=True):
        with st.form("entry_form", clear_on_submit=True):
            if data_key == "Section A":
                c1, c2 = st.columns(2)
                grade = c1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
                section = c2.text_input("Section (e.g. A, B, Blue)")
                c3, c4 = st.columns(2)
                count = c3.number_input("Student Count", min_value=1, step=1)
                needs = c4.number_input("Special Needs", min_value=0, step=1)
                entry = {"Grade": grade, "Section": section, "Students": count, "Special Needs": needs}
            
            elif data_key == "Section B":
                name = st.text_input("Teacher Full Name")
                qual = st.selectbox("Highest Degree", ["PhD", "Masters", "Bachelors", "Other"])
                exp = st.number_input("Years of Experience", min_value=0, max_value=50)
                entry = {"Teacher": name, "Degree": qual, "Experience": exp}

            elif data_key == "Section C":
                task = st.text_input("Task/Department Name")
                hours = st.number_input("Weekly Hours Required", min_value=1)
                priority = st.select_slider("Priority Level", ["Low", "Medium", "High"])
                entry = {"Task": task, "Hours": hours, "Priority": priority}

            else: # Section D
                source = st.selectbox("Feedback Source", ["Students", "Parents", "Peer"])
                rating = st.slider("Rating Score", 1, 10, 5)
                comments = st.text_area("Observations")
                entry = {"Source": source, "Rating": rating, "Comments": comments}

            if st.form_submit_button("Submit Record"):
                st.session_state.data_store[data_key].append(entry)
                st.rerun()

    # --- DATA MANAGEMENT ---
    current_data = st.session_state.data_store[data_key]
    if current_data:
        df = pd.DataFrame(current_data)
        st.subheader("Departmental Data Log")
        st.dataframe(df, use_container_width=True)
        
        # Calculate Optimization
        opt_score = calculate_optimization(data_key, current_data)
        st.metric("Optimization Index", f"{opt_score} / 200")

        c1, c2 = st.columns(2)
        with c1:
            row_to_del = st.selectbox("Select Row ID to Delete", range(len(current_data)))
            if st.button("🗑️ Delete Selected Record"):
                st.session_state.data_store[data_key].pop(row_to_del)
                st.rerun()
        
        with c2:
            st.write("### Reporting")
            if st.button("📄 Generate & Download PDF"):
                pdf_bytes = generate_pdf(menu, current_data, opt_score)
                st.download_button("Download Report", pdf_bytes, f"{data_key}_Report.pdf", "application/pdf")
    else:
        st.info("No records found in this department.")
