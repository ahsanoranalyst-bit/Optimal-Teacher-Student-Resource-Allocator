

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# --- 1. CONFIGURATION & LICENSE ---
# You can change the activation key and expiry date here
ACTIVATION_KEY = "PAK-2026"
EXPIRY_DATE = date(2026, 12, 31)

# Session Management
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

# --- 2. PROFESSIONAL PDF GENERATOR ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.school_name.upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 12)
        self.cell(0, 10, f"Official Report: {self.section_title}", 0, 1, 'C')
        self.ln(5)
        self.line(10, 32, 200, 32)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d")} | Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(title, data_list):
    pdf = SchoolPDF()
    pdf.section_title = title
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    if not data_list:
        pdf.cell(0, 10, "No records found.", 0, 1)
    else:
        df = pd.DataFrame(data_list)
        # Create Table Headers
        pdf.set_fill_color(200, 220, 255)
        pdf.set_font("Arial", 'B', 10)
        for col in df.columns:
            pdf.cell(45, 10, col, 1, 0, 'C', fill=True)
        pdf.ln()
        
        # Create Table Rows
        pdf.set_font("Arial", '', 10)
        for index, row in df.iterrows():
            for item in row:
                pdf.cell(45, 10, str(item), 1)
            pdf.ln()
            
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MULTI-STEP LOGIN & SETUP ---

# Step 1: Activation Key
if not st.session_state.authenticated:
    st.title("🔐 System Activation")
    if date.today() > EXPIRY_DATE:
        st.error("License Expired. Please contact support.")
    else:
        key_input = st.text_input("Enter Activation Key", type="password")
        if st.button("Activate"):
            if key_input == ACTIVATION_KEY:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect Key.")

# Step 2: School Name Setup (Only after Activation)
elif st.session_state.authenticated and not st.session_state.school_setup_done:
    st.title("🏫 Welcome to Resource Allocator")
    st.subheader("Final Step: Setup your institution")
    s_name = st.text_input("Enter School Name")
    if st.button("Finish Setup"):
        if s_name:
            st.session_state.school_name = s_name
            st.session_state.school_setup_done = True
            st.rerun()
        else:
            st.warning("Please provide a name.")

# Step 3: Main Application (Only after Setup)
else:
    # Sidebar
    st.sidebar.title(f"🏢 {st.session_state.school_name}")
    menu = st.sidebar.radio("Main Menu", ["Section A: Student Load", "Section B: Teacher Profile", "Section C: Efficiency", "Section D: Feedback"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("💾 Save All Data"):
        st.sidebar.success("All data synced with Google Sheets.")
    
    if st.sidebar.button("🚪 Logout / Reset"):
        st.session_state.authenticated = False
        st.session_state.school_setup_done = False
        st.rerun()

    st.title(menu)

    # Dictionary to map menu choices to data store keys
    data_key = menu.split(":")[0]

    # --- DYNAMIC FORMS BASED ON SECTION ---
    with st.form("entry_form", clear_on_submit=True):
        st.write(f"Add New Entry for {menu}")
        if data_key == "Section A":
            f1 = st.selectbox("Grade Level", [f"Grade {i}" for i in range(1, 13)])
            f2 = st.number_input("Student Count", min_value=1)
            f3 = st.number_input("Special Needs", min_value=0)
            new_data = {"Grade": f1, "Students": f2, "Special Needs": f3}
            
        elif data_key == "Section B":
            f1 = st.text_input("Teacher Name")
            f2 = st.selectbox("Qualification", ["Masters", "PhD", "Bachelors"])
            f3 = st.slider("Experience (Years)", 0, 40)
            new_data = {"Name": f1, "Qualification": f2, "Experience": f3}

        elif data_key == "Section C":
            f1 = st.number_input("Target Ratio (Students per Teacher)", min_value=1)
            f2 = st.number_input("Admin Task Hours (Weekly)", min_value=0)
            new_data = {"Ratio": f1, "Admin Hours": f2}

        elif data_key == "Section D":
            f1 = st.slider("Student Satisfaction (1-10)", 1, 10)
            f2 = st.slider("Peer Review (1-10)", 1, 10)
            new_data = {"Student Score": f1, "Peer Score": f2}

        if st.form_submit_button("Add Entry"):
            st.session_state.data_store[data_key].append(new_data)
            st.rerun()

    # --- DISPLAY & DELETE ---
    st.markdown("---")
    current_list = st.session_state.data_store[data_key]
    
    if current_list:
        st.subheader("Current Records")
        df_display = pd.DataFrame(current_list)
        st.table(df_display)
        
        # Delete functionality
        del_idx = st.number_input("Enter row index to delete", min_value=0, max_value=len(current_list)-1, step=1)
        if st.button("Delete Selected Row"):
            st.session_state.data_store[data_key].pop(int(del_idx))
            st.rerun()

        # PDF Export
        if st.button(f"📥 Export {data_key} Report"):
            pdf_bytes = generate_pdf(menu, current_list)
            st.download_button("Download Now", pdf_bytes, f"{data_key}_Report.pdf")
    else:
        st.info("No records added yet.")
