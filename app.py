

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date

# --- 1. CONFIGURATION & STATE ---
ACTIVATION_KEY = "PAK-2026"
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {"A": [], "B": [], "C": [], "Subjects": ["Math", "English", "Science"]}

# --- 2. PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, "OFFICIAL PERFORMANCE REPORT", 0, 1, 'C')
        self.ln(5)

def create_pdf(data):
    pdf = SchoolPDF()
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
    st.title("🔐 System Activation")
    if st.text_input("Enter Key", type="password") == ACTIVATION_KEY:
        if st.button("Activate"):
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    st.title("⚙️ Global Settings")
    st.session_state.school_name = st.text_input("Institution Name", "My School")
    
    st.subheader("Define Your Subjects")
    new_sub = st.text_input("Add New Subject (e.g. Urdu, Physics)")
    if st.button("Add to List") and new_sub:
        st.session_state.data_store["Subjects"].append(new_sub)
    
    st.write("Current Subjects:", st.session_state.data_store["Subjects"])
    
    if st.button("Finalize Setup"):
        st.session_state.setup_complete = True
        st.rerun()

else:
    st.sidebar.title(st.session_state.school_name)
    nav = st.sidebar.selectbox("Navigation", 
        ["Section A: Subject Analysis", "Section B: Teacher Experts", 
         "Section C: Efficiency Mapping", "Smart Analysis Dashboard"])

    # SECTION A: SUBJECT ANALYSIS
    if nav == "Section A: Subject Analysis":
        st.header("📊 Student Subject Performance")
        with st.form("a_form"):
            col1, col2 = st.columns(2)
            grade = col1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
            sec = col2.text_input("Section")
            sub = st.selectbox("Subject", st.session_state.data_store["Subjects"])
            
            c1, c2, c3, c4 = st.columns(4)
            ga, gb, gc, gd = c1.number_input("A", 0), c2.number_input("B", 0), c3.number_input("C", 0), c4.number_input("D", 0)
            
            if st.form_submit_button("Save Entry"):
                st.session_state.data_store["A"].append({
                    "Grade": grade, "Section": sec, "Subject": sub, 
                    "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd
                })
                st.rerun()

    # SECTION B: TEACHER EXPERTS
    elif nav == "Section B: Teacher Experts":
        st.header("👨‍🏫 Teacher Specialization")
        with st.form("b_form"):
            name = st.text_input("Name")
            expert_sub = st.selectbox("Specialization", st.session_state.data_store["Subjects"])
            success = st.slider("Historical Success Rate (%)", 1, 100, 75)
            if st.form_submit_button("Register Teacher"):
                st.session_state.data_store["B"].append({"Name": name, "Expertise": expert_sub, "Success": success})
                st.rerun()

    # SECTION C: EFFICIENCY MAPPING (The Brain)
    elif nav == "Section C: Efficiency Mapping":
        st.header("🎯 Solid Evidence Mapping")
        
        if not st.session_state.data_store["A"] or not st.session_state.data_store["B"]:
            st.error("Missing Data: Please fill Section A & B first.")
        else:
            # 1. Select Class & Subject
            available_classes = [f"{x['Grade']}-{x['Section']} ({x['Subject']})" for x in st.session_state.data_store["A"]]
            sel_class_str = st.selectbox("Select Target Class & Subject", available_classes)
            
            # Extract logic
            class_key = sel_class_str.split(" (")[0]
            subj_key = sel_class_str.split(" (")[1].replace(")", "")
            class_data = next(x for x in st.session_state.data_store["A"] if f"{x['Grade']}-{x['Section']}" == class_key and x['Subject'] == subj_key)
            
            # 2. Impact Calculation
            weakness_score = (class_data['C'] * 1.5) + (class_data['D'] * 2.0)
            
            # 3. Filtering Best Teachers
            experts = [t for t in st.session_state.data_store["B"] if t['Expertise'] == subj_key]
            
            if not experts:
                st.warning(f"No teachers found specialized in {subj_key}")
            else:
                best_t = sorted(experts, key=lambda x: x['Success'], reverse=True)[0]
                st.success(f"🔍 EVIDENCE: {subj_key} in {class_key} needs help. Recommended: {best_t['Name']} (Expert Score: {best_t['Success']}%)")
                
                if st.button("Deploy Teacher"):
                    impact = min(200, weakness_score * (best_t['Success']/50))
                    st.session_state.data_store["C"].append({
                        "Class": class_key, "Subject": subj_key, 
                        "Teacher": best_t['Name'], "Impact_Level": round(impact, 2)
                    })
                    st.rerun()

    # SECTION D: SMART ANALYSIS
    elif nav == "Smart Analysis Dashboard":
        st.header("📈 Efficiency Analysis Report")
        st.table(st.session_state.data_store["C"])

    # GLOBAL DATA MANAGEMENT (Row-wise Delete)
    current_key = {"Section A: Subject Analysis": "A", "Section B: Teacher Experts": "B", 
                   "Section C: Efficiency Mapping": "C"}.get(nav)
    
    if current_key and st.session_state.data_store[current_key]:
        st.markdown("---")
        df = pd.DataFrame(st.session_state.data_store[current_key])
        st.dataframe(df, use_container_width=True)
        
        idx = st.selectbox("Select row to delete", df.index)
        col1, col2 = st.columns(2)
        if col1.button("🗑️ Delete Selected"):
            st.session_state.data_store[current_key].pop(idx)
            st.rerun()
        
        pdf_bytes = create_pdf(st.session_state.data_store[current_key])
        col2.download_button("📥 Download Report", pdf_bytes, f"{nav}.pdf")
