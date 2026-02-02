

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# --- 1. SYSTEM SETTINGS ---
ACTIVATION_KEY = "PAK-2026"
EXPIRY_DATE = date(2026, 12, 31)

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'school_name' not in st.session_state: st.session_state.school_name = ""
if 'data_store' not in st.session_state:
    st.session_state.data_store = {"A": [], "B": [], "C": [], "D": [], "Demands": []}

# --- 2. PDF ENGINE ---
class SchoolReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, st.session_state.school_name.upper(), 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(report_type, data):
    pdf = SchoolReportPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    pdf.set_font('Arial', 'B', 10)
    col_width = 190 / len(df.columns)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), 1)
    pdf.ln()
    pdf.set_font('Arial', '', 9)
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, 10, str(val), 1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI LOGIC ---
if not st.session_state.authenticated:
    st.title("System Activation")
    key = st.text_input("Enter Key", type="password")
    if st.button("Activate"):
        if key == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    st.title("Institution Setup")
    s_name = st.text_input("School Name")
    if st.button("Start"):
        st.session_state.school_name = s_name
        st.session_state.setup_complete = True
        st.rerun()

else:
    st.sidebar.title(st.session_state.school_name)
    nav = st.sidebar.selectbox("Menu", 
        ["Section A: Student Grades", "Section B: Teacher Profiles", 
         "Section C: Efficiency Mapping", "Teacher Demands", "Smart Analysis"])

    # Mapping Navigation to Data Store Keys
    key_map = {
        "Section A: Student Grades": "A",
        "Section B: Teacher Profiles": "B",
        "Section C: Efficiency Mapping": "C",
        "Teacher Demands": "Demands"
    }
    current_key = key_map.get(nav)

    if nav == "Section A: Student Grades":
        with st.form("a_form"):
            grade = st.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
            sec = st.text_input("Section")
            c1, c2, c3, c4 = st.columns(4)
            ga = c1.number_input("A Grade", 0)
            gb = c2.number_input("B Grade", 0)
            gc = c3.number_input("C Grade", 0)
            gd = c4.number_input("D Grade", 0)
            if st.form_submit_button("Save"):
                st.session_state.data_store["A"].append({
                    "Grade": grade, "Section": sec, "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd
                })
                st.rerun()
        display_data = st.session_state.data_store["A"]

    elif nav == "Section B: Teacher Profiles":
        with st.form("b_form"):
            name = st.text_input("Teacher Name")
            qual = st.selectbox("Qualification", ["PhD", "Masters", "Bachelors"])
            exp = st.number_input("Experience", 0)
            if st.form_submit_button("Add"):
                st.session_state.data_store["B"].append({"Name": name, "Qual": qual, "Exp": exp})
                st.rerun()
        display_data = st.session_state.data_store["B"]

    elif nav == "Section C: Efficiency Mapping":
        t_list = [t['Name'] for t in st.session_state.data_store["B"]]
        c_list = [f"{c['Grade']}-{c['Section']}" for c in st.session_state.data_store["A"]]
        with st.form("c_form"):
            sel_t = st.selectbox("Teacher", t_list)
            sel_c = st.selectbox("Class", c_list)
            if st.form_submit_button("Link"):
                st.session_state.data_store["C"].append({"Teacher": sel_t, "Class": sel_c})
                st.rerun()
        display_data = st.session_state.data_store["C"]

    elif nav == "Teacher Demands":
        with st.form("dem_form"):
            req_t = st.text_input("Required Teacher")
            for_s = st.text_input("For Section")
            if st.form_submit_button("Log"):
                st.session_state.data_store["Demands"].append({"Teacher": req_t, "Section": for_s})
                st.rerun()
        display_data = st.session_state.data_store["Demands"]

    elif nav == "Smart Analysis":
        results = []
        for mapping in st.session_state.data_store["C"]:
            cls = next((x for x in st.session_state.data_store["A"] if f"{x['Grade']}-{x['Section']}" == mapping['Class']), None)
            if cls:
                score = min(200, (cls['C'] * 10) + (cls['D'] * 20))
                results.append({"Teacher": mapping['Teacher'], "Class": mapping['Class'], "Need_Score": f"{score}/200"})
        st.table(results)
        display_data = results

    # --- Data Management (Display & Delete) ---
    if 'display_data' in locals() and display_data:
        st.markdown("---")
        st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            # Delete Button for mistake correction
            if current_key and st.session_state.data_store[current_key]:
                if st.button("❌ Delete Last Entry"):
                    st.session_state.data_store[current_key].pop()
                    st.rerun()
        with col2:
            pdf_bytes = create_pdf(nav, display_data)
            st.download_button("📥 Download Report", pdf_bytes, f"{nav}.pdf")
