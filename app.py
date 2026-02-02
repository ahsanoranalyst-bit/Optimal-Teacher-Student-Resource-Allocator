https://g.co/gemini/share/982c97d267f2 

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date

# --- 1. SYSTEM SETTINGS ---
ACTIVATION_KEY = "PAK-2026"
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'school_name' not in st.session_state: st.session_state.school_name = ""
if 'data_store' not in st.session_state:
    st.session_state.data_store = {"A": [], "B": [], "C": [], "Demands": []}

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

def create_pdf(data):
    pdf = SchoolReportPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    pdf.set_font('Arial', 'B', 10)
    if not df.empty:
        col_width = 190 / len(df.columns)
        for col in df.columns: pdf.cell(col_width, 10, str(col), 1)
        pdf.ln()
        pdf.set_font('Arial', '', 9)
        for _, row in df.iterrows():
            for val in row: pdf.cell(col_width, 10, str(val), 1)
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

    key_map = {"Section A: Student Grades": "A", "Section B: Teacher Profiles": "B", 
               "Section C: Efficiency Mapping": "C", "Teacher Demands": "Demands"}
    current_key = key_map.get(nav)

    if nav == "Section A: Student Grades":
        with st.form("a_form"):
            grade = st.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
            sec = st.text_input("Section")
            c1, c2, c3, c4 = st.columns(4)
            ga, gb, gc, gd = c1.number_input("A", 0), c2.number_input("B", 0), c3.number_input("C", 0), c4.number_input("D", 0)
            if st.form_submit_button("Save"):
                st.session_state.data_store["A"].append({"Grade": grade, "Section": sec, "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd})
                st.rerun()
        display_data = st.session_state.data_store["A"]

    elif nav == "Section B: Teacher Profiles":
        with st.form("b_form"):
            name = st.text_input("Teacher Name")
            qual = st.selectbox("Qualification", ["PhD", "Masters", "Bachelors"])
            exp = st.number_input("Experience (Years)", 0)
            success = st.slider("Past Success Rate (%)", 1, 100, 50)
            if st.form_submit_button("Add Teacher"):
                st.session_state.data_store["B"].append({"Name": name, "Qual": qual, "Exp": exp, "Success": success})
                st.rerun()
        display_data = st.session_state.data_store["B"]

    elif nav == "Section C: Efficiency Mapping":
        st.subheader("Smart Teacher-Class Allocation")
        t_names = [t['Name'] for t in st.session_state.data_store["B"]]
        c_names = [f"{c['Grade']}-{c['Section']}" for c in st.session_state.data_store["A"]]
        
        if not t_names or not c_names:
            st.warning("Please add Teachers and Grades first.")
        else:
            sel_c = st.selectbox("Select Class", c_names)
            class_data = next(x for x in st.session_state.data_store["A"] if f"{x['Grade']}-{x['Section']}" == sel_c)
            weak_count = class_data['C'] + class_data['D']
            
            recommended = sorted(st.session_state.data_store["B"], key=lambda x: x['Success'], reverse=True)[0]
            st.info(f"💡 Advice: This class has {weak_count} weak students. Recommended: {recommended['Name']} (Success: {recommended['Success']}%)")
            
            sel_t = st.selectbox("Assign Teacher", t_names)
            if st.button("Confirm Mapping"):
                st.session_state.data_store["C"].append({"Teacher": sel_t, "Class": sel_c, "Class_Weakness": weak_count})
                st.success("Mapping Saved!")
        display_data = st.session_state.data_store["C"]

    elif nav == "Smart Analysis":
        results = []
        for mapping in st.session_state.data_store["C"]:
            teacher = next((t for t in st.session_state.data_store["B"] if t['Name'] == mapping['Teacher']), {"Name": "Unknown", "Success": 0})
            score = min(200, (mapping['Class_Weakness'] * 15)) 
            results.append({"Teacher": teacher['Name'], "Class": mapping['Class'], "Impact Score": f"{score}/200", "Success": f"{teacher['Success']}%"})
        st.table(results)
        display_data = results

    # --- 4. ADVANCED DATA MANAGEMENT (ANY ENTRY DELETE) ---
    if 'display_data' in locals() and display_data and nav != "Smart Analysis":
        st.markdown("---")
        st.subheader("Records Management")
        df_temp = pd.DataFrame(display_data)
        st.dataframe(df_temp, use_container_width=True)
        
        # Delete functionality for any specific row
        row_to_delete = st.selectbox("Select record index to delete", range(len(display_data)))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Delete Selected Entry"):
                st.session_state.data_store[current_key].pop(row_to_delete)
                st.rerun()
        with col2:
            pdf_bytes = create_pdf(display_data)
            st.download_button("📥 Download PDF Report", pdf_bytes, f"{nav}.pdf")
    
    elif nav == "Smart Analysis" and display_data:
        pdf_bytes = create_pdf(display_data)
        st.download_button("📥 Download Analysis Report", pdf_bytes, "Analysis.pdf")
