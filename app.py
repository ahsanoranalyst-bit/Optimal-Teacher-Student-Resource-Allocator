

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# --- 1. CONFIGURATION ---
ACTIVATION_KEY = "PAK-2026"
EXPIRY_DATE = date(2026, 12, 31)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'setup' not in st.session_state: st.session_state.setup = False
if 'school_name' not in st.session_state: st.session_state.school_name = ""
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Section A": [], "Section B": [], "Section C": [], "Section D": [], "Demands": []
    }

# --- 2. SMART MATCHING & DEMAND LOGIC ---
def get_smart_analysis():
    classes = st.session_state.data_store["Section A"]
    teachers = st.session_state.data_store["Section B"]
    demands = st.session_state.data_store["Demands"]
    
    if not classes or not teachers:
        return "Insufficient data for AI Matching. Please fill Section A and B."

    analysis = []
    # logic for manual demands
    for d in demands:
        analysis.append(f"📌 **Manual Demand:** {d['Requested By']} wants **{d['Teacher']}** for **{d['Class']}**.")

    # basic AI matching logic
    c_df = pd.DataFrame(classes)
    t_df = pd.DataFrame(teachers)
    
    # Matching highest experience with highest student load
    c_sorted = c_df.sort_values(by='Students', ascending=False)
    t_sorted = t_df.sort_values(by='Experience', ascending=False)
    
    for i in range(min(len(c_sorted), len(t_sorted))):
        analysis.append(f"🤖 **AI Suggestion:** Assign **{t_sorted.iloc[i]['Teacher']}** to **{c_sorted.iloc[i]['Grade']} - {c_sorted.iloc[i]['Section']}** (Load Based Match)")
    
    return analysis

# --- 3. PDF GENERATOR ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.school_name.upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 11)
        self.cell(0, 10, f"Sectional Report: {self.section_title}", 0, 1, 'C')
        self.ln(10)

def generate_pdf(title, data_list):
    pdf = SchoolPDF()
    pdf.section_title = title
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    if data_list:
        df = pd.DataFrame(data_list)
        col_width = 190 / len(df.columns)
        for col in df.columns: pdf.cell(col_width, 10, str(col), 1, 0, 'C')
        pdf.ln()
        for _, row in df.iterrows():
            for item in row: pdf.cell(col_width, 9, str(item), 1)
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 4. AUTHENTICATION & SETUP ---
if not st.session_state.auth:
    st.title("🔐 License Activation")
    if date.today() > EXPIRY_DATE: st.error("License Expired.")
    else:
        k = st.text_input("Activation Key", type="password")
        if st.button("Activate"):
            if k == ACTIVATION_KEY: st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key")

elif not st.session_state.setup:
    st.title("🏫 Institution Setup")
    sn = st.text_input("Enter School Name")
    if st.button("Start Dashboard"):
        if sn: st.session_state.school_name = sn; st.session_state.setup = True; st.rerun()

# --- 5. MAIN DASHBOARD ---
else:
    st.sidebar.title(f"🏢 {st.session_state.school_name}")
    menu = st.sidebar.selectbox("Navigate", 
        ["Section A: Student Load", "Section B: Teacher Profile", 
         "Section C: Efficiency", "Section D: Feedback", 
         "Teacher Demands", "Smart Analysis"])
    
    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.session_state.setup = False; st.rerun()

    st.title(menu)
    
    # --- SECTION A: STUDENT LOAD ---
    if menu == "Section A: Student Load":
        with st.form("a"):
            g = st.selectbox("Grade", [f"Grade {i}" for i in range(1,13)])
            s = st.text_input("Section Name (e.g. A, B, Blue)")
            stds = st.number_input("Total Students", min_value=1)
            sn = st.number_input("Special Needs", min_value=0)
            if st.form_submit_button("Add Record"):
                st.session_state.data_store["Section A"].append({"Grade": g, "Section": s, "Students": stds, "Special Needs": sn})
                st.rerun()

    # --- SECTION B: TEACHER PROFILE ---
    elif menu == "Section B: Teacher Profile":
        with st.form("b"):
            t = st.text_input("Teacher Name")
            q = st.selectbox("Qualification", ["PhD", "Masters", "Bachelors", "Other"])
            e = st.number_input("Experience (Years)", min_value=0)
            if st.form_submit_button("Add Teacher"):
                st.session_state.data_store["Section B"].append({"Teacher": t, "Qualification": q, "Experience": e})
                st.rerun()

    # --- SECTION C: EFFICIENCY ---
    elif menu == "Section C: Efficiency":
        with st.form("c"):
            tr = st.number_input("Target Teacher-Student Ratio", min_value=1)
            ah = st.number_input("Admin Hours per Week", min_value=0)
            if st.form_submit_button("Add Efficiency Data"):
                st.session_state.data_store["Section C"].append({"Target Ratio": tr, "Admin Hours": ah})
                st.rerun()

    # --- SECTION D: FEEDBACK ---
    elif menu == "Section D: Feedback":
        with st.form("d"):
            source = st.selectbox("Source", ["Student", "Parent", "Peer"])
            rating = st.slider("Rating Score", 1, 10, 5)
            comment = st.text_area("Feedback Comments")
            if st.form_submit_button("Save Feedback"):
                st.session_state.data_store["Section D"].append({"Source": source, "Rating": rating, "Comment": comment})
                st.rerun()

    # --- TEACHER DEMANDS (NEW FEATURE) ---
    elif menu == "Teacher Demands":
        st.subheader("Place a Request for a Specific Teacher")
        with st.form("demand"):
            req_by = st.text_input("Requested By (e.g. Principal, HOD)")
            t_req = st.text_input("Teacher Requested")
            c_req = st.text_input("Class/Section for this Teacher")
            if st.form_submit_button("Submit Demand"):
                st.session_state.data_store["Demands"].append({"Requested By": req_by, "Teacher": t_req, "Class": c_req})
                st.rerun()

    # --- SMART ANALYSIS PAGE ---
    elif menu == "Smart Analysis":
        st.subheader("AI and Demand-Based Recommendations")
        results = get_smart_analysis()
        if isinstance(results, list):
            for res in results: st.info(res)
        else: st.warning(results)

    # --- DATA VIEW & PDF ---
    current_key = menu.split(":")[0] if ":" in menu else menu
    if current_key in st.session_state.data_store:
        data = st.session_state.data_store[current_key]
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            if st.button("Download PDF Report"):
                pdf_bytes = generate_pdf(menu, data)
                st.download_button("Click to Download", pdf_bytes, f"{current_key}.pdf")
            
            idx = st.number_input("Delete Row Index", 0, len(data)-1, 0)
            if st.button("Delete Selected Row"):
                st.session_state.data_store[current_key].pop(idx); st.rerun()
