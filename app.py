


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
        school_name = st.session_state.data_store.get("School_Name", "GLOBAL INTERNATIONAL ACADEMY").upper()
        self.cell(0, 12, school_name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "OFFICIAL ACADEMIC PERFORMANCE & DEPLOYMENT REPORT", 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(15)

    def footer(self):
        self.set_y(-30)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "__________________________", 0, 1, 'R')
        self.cell(0, 5, "Authorized Signature & Official Stamp", 0, 1, 'R')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.cell(0, 10, f"Report Date: {timestamp} | Page {self.page_no()}", 0, 0, 'L')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 10, f"DOCUMENT SECTION: {title.upper()}", 0, 1, 'L')
    pdf.set_draw_color(31, 73, 125)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    if not df.empty:
        # کالمز کی ترتیب درست کی گئی: Predictive Score اب 5ویں نمبر پر ہے
        display_cols = ["Class", "Subject", "Teacher", "Current Score", "Predictive Score", "Status"]
        column_widths = {"Class": 25, "Subject": 35, "Teacher": 45, "Current Score": 25, "Predictive Score": 30, "Status": 30}
        
        # Header
        pdf.set_font('Arial', 'B', 8)
        pdf.set_fill_color(230, 235, 245)
        for col in display_cols:
            pdf.cell(column_widths[col], 10, col, 1, 0, 'C', fill=True)
        pdf.ln()
        
        # Data
        pdf.set_font('Arial', '', 8)
        fill = False
        for _, row in df.iterrows():
            pdf.set_fill_color(248, 248, 248) if fill else pdf.set_fill_color(255, 255, 255)
            for col in display_cols:
                # Predictive Score کالم میں ڈیٹا ڈالنے کے لیے چیک
                val = str(row.get('Current Score', '0')) if col == "Predictive Score" else str(row.get(col, ''))
                pdf.cell(column_widths[col], 9, val, 1, 0, 'C', fill=True)
            pdf.ln()
            fill = not fill
            
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
                df.columns = [str(c).strip() for c in df.columns]
                
                if upload_type == "Classes":
                    for _, row in df.iterrows():
                        key = f"{row['Grade']}-{row['Section']}"
                        subs = [s.strip() for s in str(row['Subjects']).split(",")]
                        st.session_state.data_store["Grades_Config"][key] = subs
                elif upload_type == "Student Performance":
                    for col in ['A', 'B', 'C', 'D']:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    for _, row in df.iterrows():
                        p_score = calculate_predictive_score(int(row['A']), int(row['B']), int(row['C']), int(row['D']))
                        st.session_state.data_store["A"].append({
                            "Class": str(row['Class']), "Subject": str(row['Subject']),
                            "A": int(row['A']), "B": int(row['B']), "C": int(row['C']), "D": int(row['D']),
                            "Total": int(row['A']+row['B']+row['C']+row['D']),
                            "Predictive Score": p_score
                        })
                elif upload_type == "Teachers":
                    for _, row in df.iterrows():
                        st.session_state.data_store["B"].append({
                            "Name": row['Name'], "Expertise": row['Expertise'], "Success": row['Success']
                        })
                st.sidebar.success("Data Imported Successfully!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

# --- 4. NAVIGATION & UI ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    key_input = st.text_input("Enter System Key", type="password")
    if st.button("Authenticate"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Invalid Key")

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
    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    if nav == "Student Performance (A)":
        st.header("📊 Student Performance & Prediction")
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        if class_list:
            with st.expander("➕ Add Performance Record"):
                sel_class = st.selectbox("Class", class_list)
                sel_sub = st.selectbox("Subject", st.session_state.data_store["Grades_Config"][sel_class])
                with st.form("a_form"):
                    c1,c2,c3,c4 = st.columns(4)
                    ga,gb,gc,gd = c1.number_input("A",0), c2.number_input("B",0), c3.number_input("C",0), c4.number_input("D",0)
                    if st.form_submit_button("Save & Calculate"):
                        p_score = calculate_predictive_score(ga, gb, gc, gd)
                        st.session_state.data_store["A"].append({
                            "Class": sel_class, "Subject": sel_sub,
                            "A": ga, "B": gb, "C": gc, "D": gd,
                            "Total": ga+gb+gc+gd,
                            "Predictive Score": p_score
                        })
                        st.rerun()
        
        if st.session_state.data_store["A"]:
            st.dataframe(pd.DataFrame(st.session_state.data_store["A"]), use_container_width=True)

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Faculty Expertise")
        all_subs = set()
        for s_list in st.session_state.data_store["Grades_Config"].values(): all_subs.update(s_list)
        with st.form("b_form"):
            t_name = st.text_input("Teacher Name")
            t_exp = st.selectbox("Expertise", list(all_subs) if all_subs else ["N/A"])
            t_rate = st.slider("Historical Success Rate %", 0, 100, 80)
            if st.form_submit_button("Register Teacher"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_rate})
                st.rerun()
        
        if st.session_state.data_store["B"]:
            st.dataframe(pd.DataFrame(st.session_state.data_store["B"]), use_container_width=True)

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Strategic Deployment")
        
        # خودکار پروسیس بٹن (Auto Process All)
        if st.button("🔄 Auto-Generate All Mappings from Data"):
            st.session_state.data_store["C"] = [] # Reset old mappings
            for class_data in st.session_state.data_store["A"]:
                matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == class_data['Subject']]
                if matches:
                    best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                    status = "BEST PERFORMER" if class_data['Predictive Score'] >= 60 else "NEEDS IMPROVEMENT"
                    st.session_state.data_store["C"].append({
                        "Class": class_data['Class'], "Subject": class_data['Subject'],
                        "Teacher": best_t['Name'], "Current Score": class_data['Predictive Score'],
                        "Status": status
                    })
            st.success("All class records processed automatically!")
            st.rerun()

        if st.session_state.data_store["C"]:
            mapping_df = pd.DataFrame(st.session_state.data_store["C"]).sort_values(by="Class")
            improvement_list = mapping_df[mapping_df['Status'] == "NEEDS IMPROVEMENT"].to_dict('records')
            best_list = mapping_df[mapping_df['Status'] == "BEST PERFORMER"].to_dict('records')

            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                if improvement_list:
                    pdf_imp = create_pdf(improvement_list, "Teacher Improvement List")
                    st.download_button("📥 Download ALL Improvement Records", pdf_imp, "Full_Improvement_Report.pdf")
            with c2:
                if best_list:
                    pdf_best = create_pdf(best_list, "Best Performers List")
                    st.download_button("📥 Download ALL Best Performers", pdf_best, "Full_Best_Report.pdf")

            st.write("### Current Active Mappings")
            st.dataframe(mapping_df, use_container_width=True)
