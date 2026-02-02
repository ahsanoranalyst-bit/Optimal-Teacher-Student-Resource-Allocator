

import streamlit as st
import pandas as pd
from fpdf import FPDF

# --- 1. CONFIGURATION & STATE ---
ACTIVATION_KEY = "PAK-2026"
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {"A": [], "B": [], "C": [], "Grades": {}, "School": ""}

# --- 2. PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, st.session_state.school_name.upper(), 0, 1, 'C')
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
    key_input = st.text_input("Enter Key", type="password")
    if st.button("Activate"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid Key")

elif not st.session_state.setup_complete:
    st.title("⚙️ Global Institution Setup")
    st.session_state.school_name = st.text_input("Institution Name", "My School")
    
    st.subheader("Step 1: Define Grades & Their Subjects")
    g_name = st.selectbox("Select Grade to Setup", [f"Grade {i}" for i in range(1, 13)])
    sub_list = st.text_area("Enter Subjects for this Grade (separated by comma)", "Math, English, Urdu")
    
    if st.button("Save Grade Configuration"):
        subjects = [s.strip() for s in sub_list.split(",")]
        st.session_state.data_store["Grades"][g_name] = subjects
        st.success(f"Configured {g_name} with {len(subjects)} subjects.")
    
    st.write("Current Configuration:", st.session_state.data_store["Grades"])
    
    if st.session_state.data_store["Grades"] and st.button("Finalize Setup & Start"):
        st.session_state.setup_complete = True
        st.rerun()

else:
    st.sidebar.title(st.session_state.school_name)
    nav = st.sidebar.selectbox("Navigation", 
        ["Section A: Student Performance", "Section B: Teacher Experts", 
         "Section C: Efficiency Mapping", "Analysis Dashboard"])

    # SECTION A
    if nav == "Section A: Student Performance":
        st.header("📊 Student Subject Performance")
        with st.form("a_form"):
            sel_g = st.selectbox("Grade", list(st.session_state.data_store["Grades"].keys()))
            sec = st.text_input("Section (e.g., A)")
            sub = st.selectbox("Subject", st.session_state.data_store["Grades"][sel_g])
            
            c1, c2, c3, c4 = st.columns(4)
            ga, gb, gc, gd = c1.number_input("A", 0), c2.number_input("B", 0), c3.number_input("C", 0), c4.number_input("D", 0)
            
            if st.form_submit_button("Save Performance Data"):
                st.session_state.data_store["A"].append({
                    "Grade": sel_g, "Section": sec, "Subject": sub, 
                    "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd
                })
                st.rerun()

    # SECTION B
    elif nav == "Section B: Teacher Experts":
        st.header("👨‍🏫 Teacher Specialization")
        all_subs = []
        for s in st.session_state.data_store["Grades"].values(): all_subs.extend(s)
        unique_subs = list(set(all_subs))

        with st.form("b_form"):
            t_name = st.text_input("Teacher Name")
            expert_sub = st.selectbox("Specialization", unique_subs)
            success = st.slider("Success Rate (%)", 1, 100, 75)
            if st.form_submit_button("Register Teacher"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": expert_sub, "Success": success})
                st.rerun()

    # SECTION C
    elif nav == "Section C: Efficiency Mapping":
        st.header("🎯 Evidence-Based Mapping")
        if not st.session_state.data_store["A"] or not st.session_state.data_store["B"]:
            st.warning("Please enter Student Data and Teacher Profiles first.")
        else:
            class_options = [f"{x['Grade']}-{x['Section']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
            sel_entry = st.selectbox("Select Class to Analyze", class_options)
            
            # Extract selected data
            parts = sel_entry.split(" | ")
            g_sec = parts[0]
            subj = parts[1]
            
            c_data = next(x for x in st.session_state.data_store["A"] if f"{x['Grade']}-{x['Section']}" == g_sec and x['Subject'] == subj)
            weakness = (c_data['C'] * 1.5) + (c_data['D'] * 2.5)
            
            experts = [t for t in st.session_state.data_store["B"] if t['Expertise'] == subj]
            if experts:
                best_t = sorted(experts, key=lambda x: x['Success'], reverse=True)[0]
                st.info(f"💡 Recommendation: {best_t['Name']} is best for {subj} in {g_sec}")
                if st.button("Confirm Deployment"):
                    impact = min(200, weakness * (best_t['Success']/50))
                    st.session_state.data_store["C"].append({
                        "Class": g_sec, "Subject": subj, "Teacher": best_t['Name'], "Efficiency_Score": round(impact, 2)
                    })
                    st.rerun()
            else:
                st.error(f"No teacher found for {subj}")

    # DATA MANAGEMENT
    current_key = {"Section A: Student Performance": "A", "Section B: Teacher Experts": "B", 
                   "Section C: Efficiency Mapping": "C"}.get(nav)
    
    if current_key and st.session_state.data_store[current_key]:
        st.markdown("---")
        df = pd.DataFrame(st.session_state.data_store[current_key])
        st.dataframe(df, use_container_width=True)
        idx = st.selectbox("Select row to delete", df.index)
        if st.button("🗑️ Delete Record"):
            st.session_state.data_store[current_key].pop(idx)
            st.rerun()
