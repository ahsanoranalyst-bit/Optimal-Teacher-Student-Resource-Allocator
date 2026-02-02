import streamlit as st
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# --- 1. CORE INITIALIZATION ---
ACTIVATION_KEY = "PAK-2026"

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Grades_Config": {}, 
        "A": [],             
        "B": [],             
        "C": [],             
        "School_Name": ""
    }

# --- 2. PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        name = st.session_state.data_store.get("School_Name", "SCHOOL REPORT")
        self.cell(0, 10, name.upper(), 0, 1, 'C')
        self.ln(5)

def create_pdf(data, title="Report"):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Section: {title}", 0, 1, 'L')
    pdf.ln(5)
    
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
    st.title("🔐 Secure Activation")
    key_input = st.text_input("Enter System Key", type="password")
    if st.button("Activate System"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Invalid Access Key")

elif not st.session_state.setup_complete:
    st.title("⚙️ School Configuration")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "My Institution")
    
    st.subheader("Step 1: Class Setup")
    c1, c2 = st.columns(2)
    g_name = c1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
    s_name = c2.text_input("Section Name (e.g., A, B, Blue)")
    sub_input = st.text_area("Subjects (separated by comma)", "Math, English, Science")
    
    if st.button("Add This Class Configuration"):
        if s_name:
            full_key = f"{g_name}-{s_name}"
            subjects = [s.strip() for s in sub_input.split(",") if s.strip()]
            st.session_state.data_store["Grades_Config"][full_key] = subjects
            st.success(f"✅ Added {full_key}")
    
    if st.session_state.data_store["Grades_Config"]:
        if st.button("🚀 Finalize & Go to Dashboard"):
            st.session_state.setup_complete = True
            st.rerun()

else:
    st.sidebar.title(st.session_state.data_store["School_Name"])
    nav = st.sidebar.selectbox("Main Navigation", 
        ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)", "Institution Summary"])

    if nav == "Student Performance (A)":
        st.header("📊 Input Student Grades")
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        sel_class = st.selectbox("Select Class-Section", class_list)
        sel_sub = st.selectbox("Select Subject", st.session_state.data_store["Grades_Config"][sel_class])
        
        with st.form("a_form"):
            c1, c2, c3, c4 = st.columns(4)
            ga, gb, gc, gd = c1.number_input("A", 0), c2.number_input("B", 0), c3.number_input("C", 0), c4.number_input("D", 0)
            if st.form_submit_button("Save Performance Data"):
                st.session_state.data_store["A"].append({"Class": sel_class, "Subject": sel_sub, "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd})
                st.rerun()
        display_key = "A"

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Teacher Specialization")
        all_subs = set()
        for s_list in st.session_state.data_store["Grades_Config"].values(): all_subs.update(s_list)
        with st.form("b_form"):
            t_name = st.text_input("Full Name")
            t_exp = st.selectbox("Specialized Subject", list(all_subs))
            t_rate = st.slider("Success Rate (%)", 1, 100, 70)
            if st.form_submit_button("Register Teacher"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_rate})
                st.rerun()
        display_key = "B"

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Solid Evidence & Allocation")
        if not st.session_state.data_store["A"] or not st.session_state.data_store["B"]:
            st.warning("Complete Section A and B first.")
        else:
            options = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
            sel = st.selectbox("Select Class/Subject", options)
            parts = sel.split(" | ")
            target_data = next(x for x in st.session_state.data_store["A"] if x['Class'] == parts[0] and x['Subject'] == parts[1])
            
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == parts[1]]
            if matches:
                best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                assigned_count = len([c for c in st.session_state.data_store["C"] if c['Teacher'] == best_t['Name']])
                st.info(f"💡 Recommended: {best_t['Name']} | Workload: {assigned_count} Classes")
                if st.button("Confirm Deployment"):
                    impact = min(200, ((target_data['C']*1.5 + target_data['D']*2.5) * (best_t['Success']/40)))
                    st.session_state.data_store["C"].append({"Class": parts[0], "Subject": parts[1], "Teacher": best_t['Name'], "Impact": round(impact, 2)})
                    st.rerun()
        display_key = "C"

    elif nav == "Institution Summary":
        st.header("🏫 Principal's Executive Dashboard")
        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            
            # Visual 1: Grades Chart
            total_grades = df_a[['A', 'B', 'C', 'D']].sum().reset_index()
            total_grades.columns = ['Grade', 'Count']
            fig_grades = px.bar(total_grades, x='Grade', y='Count', title="Overall School Performance", color='Grade')
            st.plotly_chart(fig_grades)
            
            # Visual 2: Critical Subjects
            df_a['Weakness'] = df_a['C'] + df_a['D']
            fig_weak = px.pie(df_a, values='Weakness', names='Subject', title="Critical Subjects (High C/D Grades)")
            st.plotly_chart(fig_weak)

            if st.session_state.data_store["C"]:
                st.subheader("Final Deployment Summary")
                df_final = pd.DataFrame(st.session_state.data_store["C"])
                st.dataframe(df_final, use_container_width=True)
                
                pdf_report = create_pdf(st.session_state.data_store["C"], title="Executive Deployment Summary")
                st.download_button("📥 Download Summary PDF", pdf_report, "Principal_Summary.pdf")
        else:
            st.info("Input student performance (A) to see the summary.")
        display_key = None

    # --- SHARED TABLE VIEW ---
    if 'display_key' in locals() and display_key and st.session_state.data_store[display_key]:
        st.markdown("---")
        df_show = pd.DataFrame(st.session_state.data_store[display_key])
        st.dataframe(df_show, use_container_width=True)
        pdf_bytes = create_pdf(st.session_state.data_store[display_key], title=nav)
        st.download_button(f"📥 Download {nav} PDF", pdf_bytes, f"{nav}.pdf")
