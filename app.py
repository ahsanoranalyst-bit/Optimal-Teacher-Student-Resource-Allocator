


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
    score = ((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total
    return round(score, 2)

# --- 2. PROFESSIONAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        name = st.session_state.data_store.get("School_Name", "ACADEMY").upper()
        self.cell(0, 12, name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "OFFICIAL PERFORMANCE REPORT", 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(15)

    def footer(self):
        self.set_y(-30)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "__________________________", 0, 1, 'R')
        self.cell(0, 5, "Authorized Signature & Stamp", 0, 1, 'R')
        ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.cell(0, 10, f"Date: {ts} | Page {self.page_no()}", 0, 0, 'L')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"SECTION: {title.upper()}", 0, 1, 'L')
    pdf.ln(5)
    if not df.empty:
        pdf.set_font('Arial', 'B', 8)
        w = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(w, 10, str(col), 1, 0, 'C')
        pdf.ln()
        pdf.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            for col in df.columns:
                pdf.cell(w, 9, str(row[col]), 1, 0, 'C')
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
                        st.session_state.data_store["B"].append({"Name": row['Name'], "Expertise": row['Expertise'], "Success": row['Success']})
                st.sidebar.success("Import Successful!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

# --- 4. NAVIGATION & UI ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    pwd = st.text_input("Enter Key", type="password")
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
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)", "Teacher Portal"])

    # --- SECTION A: PERFORMANCE ---
    if nav == "Student Performance (A)":
        st.header("📊 Performance Records")
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        if class_list:
            with st.expander("➕ Manual Entry"):
                sel_class = st.selectbox("Class", class_list)
                sel_sub = st.selectbox("Subject", st.session_state.data_store["Grades_Config"][sel_class])
                with st.form("a_form"):
                    c1,c2,c3,c4 = st.columns(4)
                    ga,gb,gc,gd = c1.number_input("A",0), c2.number_input("B",0), c3.number_input("C",0), c4.number_input("D",0)
                    if st.form_submit_button("Save"):
                        score = calculate_predictive_score(ga, gb, gc, gd)
                        st.session_state.data_store["A"].append({
                            "Class": sel_class, "Subject": sel_sub,
                            "A": ga, "B": gb, "C": gc, "D": gd, "Predictive Score": score
                        })
                        st.rerun()
        
        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_a)
            idx_to_del = st.selectbox("Select Record ID to Delete", df_a.index)
            if st.button("🗑️ Delete Selected Record"):
                st.session_state.data_store["A"].pop(idx_to_del)
                st.rerun()

    # --- SECTION B: TEACHERS ---
    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Teacher Registration")
        with st.form("t_form"):
            t_name = st.text_input("Teacher Name")
            t_exp = st.text_input("Expertise (e.g. Math)")
            t_success = st.number_input("Success Rate (%)", 0, 100)
            if st.form_submit_button("Register"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_success})
                st.rerun()
        
        if st.session_state.data_store["B"]:
            df_b = pd.DataFrame(st.session_state.data_store["B"])
            st.dataframe(df_b)
            idx_to_del_b = st.selectbox("Select Teacher ID to Delete", df_b.index)
            if st.button("🗑️ Delete Teacher"):
                st.session_state.data_store["B"].pop(idx_to_del_b)
                st.rerun()

    # --- SECTION C: MAPPING & PDF ---
    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Efficiency Mapping & Reports")
        if st.button("🔄 Auto-Map All Classes"):
            st.session_state.data_store["C"] = []
            for record in st.session_state.data_store["A"]:
                matches = [t for t in st.session_state.data_store["B"] if t['Expertise'].lower() == record['Subject'].lower()]
                if matches:
                    best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                    status = "BEST TEACHER" if record['Predictive Score'] >= 70 else "IMPROVEMENT NEEDED"
                    st.session_state.data_store["C"].append({
                        "Class": record['Class'], "Subject": record['Subject'], 
                        "Teacher": best_t['Name'], "Score": record['Predictive Score'], "Status": status
                    })
            st.success("Mapping Processed!")

        if st.session_state.data_store["C"]:
            df_c = pd.DataFrame(st.session_state.data_store["C"])
            st.dataframe(df_c)
            
            best_df = df_c[df_c["Status"] == "BEST TEACHER"]
            improve_df = df_c[df_c["Status"] == "IMPROVEMENT NEEDED"]
            
            col1, col2 = st.columns(2)
            with col1:
                if not best_df.empty:
                    st.success(f"Best Found: {len(best_df)}")
                    st.download_button("📥 Download Best PDF", create_pdf(best_df, "BEST TEACHERS"), "Best_Performers.pdf")
            with col2:
                if not improve_df.empty:
                    st.warning(f"Improvement Needed: {len(improve_df)}")
                    st.download_button("📥 Download Improvement PDF", create_pdf(improve_df, "IMPROVEMENT"), "Improvement_List.pdf")

    # --- SECTION D: TEACHER PORTAL ---
    elif nav == "Teacher Portal":
        st.header("📜 Teacher Personal Portal")
        if st.session_state.data_store["B"]:
            names = list(set([t['Name'] for t in st.session_state.data_store["B"]]))
            selected = st.selectbox("Select Teacher to View Reports", names)
            
            # Find classes assigned to this teacher in Mapping C
            report_data = [x for x in st.session_state.data_store["C"] if x['Teacher'] == selected]
            
            if report_data:
                st.subheader(f"Performance Data for: {selected}")
                st.dataframe(pd.DataFrame(report_data))
                st.download_button(f"📥 Download {selected}'s PDF", create_pdf(report_data, f"REPORT: {selected}"), f"{selected}_Report.pdf")
            else:
                st.info("No mapping data found for this teacher. Please run 'Auto-Map' in Section C first.")
