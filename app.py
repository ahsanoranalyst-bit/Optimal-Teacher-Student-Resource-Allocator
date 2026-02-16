import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. CORE INITIALIZATION ---
ACTIVATION_KEY = "PAK-2026"

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Grades_Config": {},
        "A": [], "B": [], "C": [],
        "School_Name": "Global International Academy"
    }

# --- PREDICTIVE ENGINE ---
def calculate_predictive_score(a, b, c, d):
    total = a + b + c + d
    if total == 0: return 0
    # Predictive Score as the 5th point logic
    score = ((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total
    return round(score, 2)

# --- 2. PROFESSIONAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        name = st.session_state.data_store.get("School_Name", "ACADEMY").upper()
        self.cell(0, 12, name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "OFFICIAL PERFORMANCE REPORT", 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(20)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, "Authorized Signature: __________________________", 0, 1, 'R')
        ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.cell(0, 10, f"Date: {ts} | Page {self.page_no()}", 0, 0, 'L')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"REPORT: {title.upper()}", 0, 1, 'L')
    pdf.ln(5)
    if not df.empty:
        # Adjusted width for more columns
        w = 190 / len(df.columns)
        pdf.set_font('Arial', 'B', 7)
        pdf.set_fill_color(230, 230, 230)
        for col in df.columns:
            pdf.cell(w, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        pdf.set_font('Arial', '', 6)
        for _, row in df.iterrows():
            for col in df.columns:
                pdf.cell(w, 8, str(row[col]), 1, 0, 'C')
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. BULK UPLOAD LOGIC ---
def handle_bulk_upload():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Excel Data Import")
    upload_type = st.sidebar.selectbox("Category", ["Classes", "Student Performance", "Teachers"], key="upload_sel")
    uploaded_file = st.sidebar.file_uploader(f"Choose {upload_type} Excel File", type=["xlsx"], key="file_up")

    if uploaded_file is not None:
        if st.sidebar.button(f"Confirm Import: {upload_type}"):
            try:
                df = pd.read_excel(uploaded_file).fillna('')
                if upload_type == "Classes":
                    for _, row in df.iterrows():
                        key = f"{row['Grade']}-{row['Section']}"
                        st.session_state.data_store["Grades_Config"][key] = [s.strip() for s in str(row['Subjects']).split(",")]
                elif upload_type == "Student Performance":
                    for _, row in df.iterrows():
                        p_score = calculate_predictive_score(int(row['A']), int(row['B']), int(row['C']), int(row['D']))
                        st.session_state.data_store["A"].append({
                            "Class": str(row['Class']), "Subject": str(row['Subject']),
                            "A": int(row['A']), "B": int(row['B']), "C": int(row['C']), "D": int(row['D']),
                            "Predictive Score": p_score
                        })
                elif upload_type == "Teachers":
                    for _, row in df.iterrows():
                        st.session_state.data_store["B"].append({
                            "Name": row['Name'],
                            "Expertise": row['Expertise'],
                            "Success": int(row['Success']),
                            "Assigned Class": str(row['Assigned Class'])
                        })
                st.sidebar.success("Import Successful!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

# --- 4. MAIN INTERFACE ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    pwd = st.text_input("Enter Activation Key", type="password")
    if st.button("Login"):
        if pwd == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    handle_bulk_upload()
    st.title("⚙️ Institution Setup")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "Global International Academy")
    
    st.subheader("Manual Class Configuration")
    c1, c2 = st.columns(2)
    g_name = c1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
    s_name = c2.text_input("Section")
    sub_input = st.text_area("Subjects (comma separated)", "Math, English, Science")
    
    if st.button("Save Class"):
        if s_name:
            full_key = f"{g_name}-{s_name}"
            subjects = [s.strip() for s in sub_input.split(",") if s.strip()]
            st.session_state.data_store["Grades_Config"][full_key] = subjects
            st.success(f"Added {full_key}")
    
    if st.session_state.data_store["Grades_Config"]:
        if st.button("🚀 Enter Dashboard"):
            st.session_state.setup_complete = True
            st.rerun()
else:
    st.sidebar.title("🎮 Dashboard Menu")
    nav = st.sidebar.radio("Go To:", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)", "Teacher Portal"])
    handle_bulk_upload()

    if st.sidebar.button("🔓 Logout"):
        st.session_state.authenticated = False
        st.session_state.setup_complete = False
        st.rerun()

    st.title(f"🏫 {st.session_state.data_store['School_Name']}")

    if nav == "Student Performance (A)":
        st.header("📊 Student Performance Records")
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        with st.expander("➕ Add Manual Entry"):
            if class_list:
                sel_class = st.selectbox("Select Class", class_list)
                sel_sub = st.selectbox("Select Subject", st.session_state.data_store["Grades_Config"][sel_class])
                with st.form("manual_a_form"):
                    c1,c2,c3,c4 = st.columns(4)
                    ga, gb, gc, gd = c1.number_input("A", 0), c2.number_input("B", 0), c3.number_input("C", 0), c4.number_input("D", 0)
                    if st.form_submit_button("Save Record"):
                        score = calculate_predictive_score(ga, gb, gc, gd)
                        st.session_state.data_store["A"].append({
                            "Class": sel_class, "Subject": sel_sub,
                            "A": ga, "B": gb, "C": gc, "D": gd, "Predictive Score": score
                        })
                        st.rerun()

        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_a)
            idx = st.selectbox("Select Record ID to Delete", df_a.index)
            if st.button("🗑️ Delete Record"):
                st.session_state.data_store["A"].pop(idx)
                st.rerun()

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Teacher Registry")
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        with st.form("manual_t_form"):
            t_name = st.text_input("Name")
            t_exp = st.text_input("Expertise")
            t_class = st.selectbox("Assigned Class", class_list) if class_list else st.text_input("Assigned Class")
            t_success = st.number_input("Success Rate (Past Record)", 0, 100)
            if st.form_submit_button("Register"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_success, "Assigned Class": t_class})
                st.rerun()

        if st.session_state.data_store["B"]:
            df_b = pd.DataFrame(st.session_state.data_store["B"])
            st.dataframe(df_b)
            idx_b = st.selectbox("Select Teacher ID to Delete", df_b.index)
            if st.button("🗑️ Remove Teacher"):
                st.session_state.data_store["B"].pop(idx_b)
                st.rerun()

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Efficiency Mapping & Action Plans")
        if st.button("🔄 Auto-Map Teachers"):
            st.session_state.data_store["C"] = []
            for teacher in st.session_state.data_store["B"]:
                relevant = [a for a in st.session_state.data_store["A"]
                           if a['Subject'].lower() == teacher['Expertise'].lower()
                           and a['Class'] == teacher['Assigned Class']]
                
                if relevant:
                    for r in relevant:
                        # --- SMART LOGIC INTEGRATION ---
                        t_success = teacher['Success']
                        p_score = r['Predictive Score']
                        
                        # Weighted Calculation: 60% Class Results, 40% Teacher History
                        combined_index = (p_score * 0.6) + (t_success * 0.4)
                        
                        # Diagnostic Logic
                        if combined_index >= 85:
                            status = "GOLD STANDARD"
                            action = "Promote as Mentor"
                        elif p_score < 50 and t_success < 50:
                            status = "CRITICAL: DOUBLE ACTION"
                            action = "Teacher Training & Remedial Student Classes"
                        elif p_score < 50 and t_success >= 70:
                            status = "CLASS AT RISK"
                            action = "Focus on Student Basics / Extra Classes"
                        elif p_score >= 70 and t_success < 50:
                            status = "SKILL GAP"
                            action = "Teacher Subject-Matter Training Required"
                        elif combined_index >= 70:
                            status = "BEST TEACHER"
                            action = "Maintain Performance"
                        else:
                            status = "IMPROVEMENT NEEDED"
                            action = "Closer Monitoring Required"

                        st.session_state.data_store["C"].append({
                            "Class": r['Class'], "Subject": teacher['Expertise'], "Teacher": teacher['Name'],
                            "Teacher Success": t_success, "Student Score": p_score, 
                            "Efficiency Index": round(combined_index, 2), "Status": status, "Action Plan": action
                        })
                else:
                    st.session_state.data_store["C"].append({
                        "Class": teacher['Assigned Class'], "Subject": teacher['Expertise'], "Teacher": teacher['Name'],
                        "Teacher Success": teacher['Success'], "Student Score": 0, 
                        "Efficiency Index": 0, "Status": "NO CURRENT DATA", "Action Plan": "Conduct Assessment"
                    })
            st.success("Mapping Completed with Smart Action Plans!")

        if st.session_state.data_store["C"]:
            df_c = pd.DataFrame(st.session_state.data_store["C"])
            st.dataframe(df_c)
            best = df_c[df_c["Status"].isin(["BEST TEACHER", "GOLD STANDARD"])]
            improve = df_c[~df_c["Status"].isin(["BEST TEACHER", "GOLD STANDARD"])]
            col1, col2 = st.columns(2)
            with col1: st.download_button("📥 Download Excellence Report", create_pdf(best, "Excellence Report"), "Excellence.pdf")
            with col2: st.download_button("📥 Download Action Plan Report", create_pdf(improve, "Required Actions"), "Action_Plan.pdf")

    elif nav == "Teacher Portal":
        st.header("📜 Comprehensive Teacher Report")
        if st.session_state.data_store["B"]:
            t_names = list(set([t['Name'] for t in st.session_state.data_store["B"]]))
            sel_t = st.selectbox("Select Teacher", t_names)
            
            # Filtering all records for this specific teacher across different classes
            t_data = [x for x in st.session_state.data_store["C"] if x['Teacher'] == sel_t]
            
            if t_data:
                st.subheader(f"Performance Summary for {sel_t}")
                st.dataframe(pd.DataFrame(t_data))
                st.download_button(f"📥 Download Full Profile: {sel_t}", create_pdf(t_data, f"Individual Analysis: {sel_t}"), f"{sel_t}_Report.pdf")
            else:
                st.info("No mapped data found for this teacher. Please run 'Auto-Map Teachers' in Efficiency Mapping.")
