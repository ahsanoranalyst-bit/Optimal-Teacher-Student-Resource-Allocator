
import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# --- 1. SYSTEM SETTINGS ---
ACTIVATION_KEY = "PAK-2026"
EXPIRY_DATE = date(2026, 12, 31)

# Initialize Session State
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'school_name' not in st.session_state: st.session_state.school_name = ""
if 'data_store' not in st.session_state:
    st.session_state.data_store = {"A": [], "B": [], "C": [], "D": [], "Demands": []}

# --- 2. PROFESSIONAL PDF ENGINE ---
class SchoolReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, st.session_state.school_name.upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"Section Report: {self.report_type}", 0, 1, 'C')
        self.ln(5)
        self.line(10, 30, 200, 30)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d")} | Page {self.page_no()}', 0, 0, 'C')

def create_pdf(report_type, data):
    pdf = SchoolReportPDF()
    pdf.report_type = report_type
    pdf.add_page()
    if not data:
        pdf.cell(0, 10, "No records found.", 0, 1)
    else:
        df = pd.DataFrame(data)
        pdf.set_fill_color(220, 220, 220)
        pdf.set_font('Arial', 'B', 8)
        col_width = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        pdf.set_font('Arial', '', 7)
        for _, row in df.iterrows():
            for val in row:
                pdf.cell(col_width, 9, str(val), 1)
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. ACCESS CONTROL ---
if not st.session_state.authenticated:
    st.title("🔐 System Activation")
    key = st.text_input("Enter Activation Key", type="password")
    if st.button("Activate"):
        if key == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Invalid Key")

elif not st.session_state.setup_complete:
    st.title("🏫 Institution Setup")
    s_name = st.text_input("Enter School Name")
    if st.button("Continue to Dashboard"):
        if s_name:
            st.session_state.school_name = s_name
            st.session_state.setup_complete = True
            st.rerun()

# --- 4. MAIN DASHBOARD ---
else:
    st.sidebar.title(f"🏢 {st.session_state.school_name}")
    nav = st.sidebar.selectbox("Navigation", 
        ["Section A: Student Load", "Section B: Teacher Profiles", 
         "Section C: Efficiency Mapping", "Section D: Feedback", 
         "Teacher Demands", "Smart Analysis Report"])
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.setup_complete = False
        st.rerun()

    st.title(nav)

    # --- SECTION A: STUDENT LOAD ---
    if nav == "Section A: Student Load":
        with st.form("a_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            grade = c1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
            section = c2.text_input("Section Name (e.g. A, B, Blue)")
            total = st.number_input("Total Students", min_value=1)
            special = st.number_input("Special Needs Students (Attention Required)", min_value=0)
            details = st.text_area("Specific Needs Description (Mental Load Detail)")
            if st.form_submit_button("Save Class Data"):
                st.session_state.data_store["A"].append({
                    "Grade": grade, "Section": section, "Total": total, "Special_Needs": special, "Details": details
                })
                st.rerun()
        display_data = st.session_state.data_store["A"]

    # --- SECTION B: TEACHER PROFILES (UPDATED WITH QUALIFICATION) ---
    elif nav == "Section B: Teacher Profiles":
        with st.form("b_form", clear_on_submit=True):
            t_name = st.text_input("Teacher Name")
            t_qual = st.selectbox("Qualification", ["PhD", "Masters", "Bachelors", "Diploma"])
            t_exp = st.number_input("Experience (Years)", min_value=0)
            if st.form_submit_button("Add Teacher Profile"):
                st.session_state.data_store["B"].append({
                    "Name": t_name, "Qualification": t_qual, "Experience": t_exp
                })
                st.rerun()
        display_data = st.session_state.data_store["B"]

    # --- SECTION C: EFFICIENCY MAPPING ---
    elif nav == "Section C: Efficiency Mapping":
        if not st.session_state.data_store["A"] or not st.session_state.data_store["B"]:
            st.warning("Please add data in Section A and B first.")
        else:
            with st.form("c_form", clear_on_submit=True):
                t_list = [t['Name'] for t in st.session_state.data_store["B"]]
                c_list = [f"{c['Grade']}-{c['Section']}" for c in st.session_state.data_store["Classes"] if 'Grade' in c] # Safety check
                # Note: Fix for the list comprehension below
                c_list = [f"{c['Grade']}-{c['Section']}" for c in st.session_state.data_store["A"]]
                
                sel_t = st.selectbox("Select Teacher", t_list)
                sel_c = st.selectbox("Assign to Section", c_list)
                per = st.number_input("Periods per Week", min_value=1)
                adm = st.number_input("Weekly Admin Hours", value=1)
                if st.form_submit_button("Link Resource"):
                    st.session_state.data_store["C"].append({
                        "Teacher": sel_t, "Class": sel_c, "Periods": per, "Admin_Hours": adm
                    })
                    st.rerun()
        display_data = st.session_state.data_store["C"]

    # --- TEACHER DEMANDS ---
    elif nav == "Teacher Demands":
        with st.form("demand_form", clear_on_submit=True):
            req_by = st.text_input("Requester Name")
            req_t = st.text_input("Teacher Requested")
            req_s = st.text_input("For Section")
            if st.form_submit_button("Log Demand"):
                st.session_state.data_store["Demands"].append({"By": req_by, "Teacher": req_t, "Section": req_s})
                st.rerun()
        display_data = st.session_state.data_store["Demands"]

    # --- SMART ANALYSIS (HIGHLY LOGICAL MATCHING) ---
    elif nav == "Smart Analysis Report":
        analysis = []
        qual_weight = {"PhD": 40, "Masters": 30, "Bachelors": 20, "Diploma": 10}
        
        for entry in st.session_state.data_store["C"]:
            # Get Teacher Data
            t_data = next((t for t in st.session_state.data_store["B"] if t['Name'] == entry['Teacher']), None)
            # Get Class Data
            cls_data = next((x for x in st.session_state.data_store["A"] if f"{x['Grade']}-{x['Section']}" == entry['Class']), None)
            
            # Logic: Load vs Capability
            load = (entry['Periods'] * 5) + (entry['Admin_Hours'] * 5) + (cls_data['Special_Needs'] * 10 if cls_data else 0)
            strength = qual_weight.get(t_data['Qualification'], 0) + (t_data['Experience'] * 2) if t_data else 0
            
            # Efficiency Score (1-200)
            score = min(200, max(1, int((load / (strength if strength > 0 else 1)) * 50)))
            
            analysis.append({
                "Teacher": entry['Teacher'], 
                "Qualification": t_data['Qualification'] if t_data else "N/A",
                "Class": entry['Class'], 
                "Score_Index": f"{score}/200", 
                "Match_Status": "Perfect Match" if score < 100 else "High Pressure"
            })
        st.subheader("Resource Matching & Intelligence Index")
        if analysis: st.table(analysis)
        display_data = analysis

    # --- SECTION D: FEEDBACK ---
    else:
        with st.form("d_form"):
            f_t = st.text_input("Teacher Name")
            f_r = st.slider("Rating", 1, 10)
            if st.form_submit_button("Save Feedback"):
                st.session_state.data_store["D"].append({"Teacher": f_t, "Rating": f_r})
                st.rerun()
        display_data = st.session_state.data_store["D"]

    # --- DATA MANAGEMENT & PDF ---
    if 'display_data' in locals() and display_data:
        st.markdown("---")
        st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Delete Last Entry"):
                key_map = {"Section A": "A", "Section B": "B", "Section C": "C", "Teacher Demands": "Demands", "Section D": "D"}
                key = key_map.get(nav.split(":")[0], "Demands" if "Demands" in nav else "C")
                if st.session_state.data_store[key]:
                    st.session_state.data_store[key].pop()
                    st.rerun()
        with c2:
            pdf_bytes = create_pdf(nav, display_data)
            st.download_button(f"📥 Download {nav} PDF", pdf_bytes, f"{nav}.pdf")
