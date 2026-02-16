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
    pdf.cell(0, 10, f"SECTION: {title.upper()}", 0, 1, 'L')
    pdf.set_draw_color(31, 73, 125)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    if not df.empty:
        column_widths = {"Class": 25, "Subject": 35, "Teacher": 45, "Current Score": 35, "Status": 50}
        display_cols = ["Class", "Subject", "Teacher", "Current Score", "Status"]
        
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(230, 235, 245)
        for col in display_cols:
            pdf.cell(column_widths[col], 10, col, 1, 0, 'C', fill=True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 9)
        fill = False
        for _, row in df.iterrows():
            pdf.set_fill_color(248, 248, 248) if fill else pdf.set_fill_color(255, 255, 255)
            x_b, y_b = pdf.get_x(), pdf.get_y()
            for col in display_cols:
                val = str(row[col])
                pdf.multi_cell(column_widths[col], 10, val, 1, 'C', fill=True)
                pdf.set_xy(x_b + column_widths[col], y_b)
                x_b += column_widths[col]
            pdf.ln(10)
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
    
    if st.button("🚀 Enter Dashboard"):
        st.session_state.setup_complete = True
        st.rerun()

else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    if nav == "Student Performance (A)":
        st.header("📊 Student Performance & Prediction")
        if st.session_state.data_store["A"]:
            st.dataframe(pd.DataFrame(st.session_state.data_store["A"]), use_container_width=True)

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Faculty Expertise")
        if st.session_state.data_store["B"]:
            st.dataframe(pd.DataFrame(st.session_state.data_store["B"]), use_container_width=True)

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Strategic Deployment & Auto-Reporting")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("⚡ Run Automatic Mapping (All Classes)"):
                st.session_state.data_store["C"] = [] # Reset old mapping
                for record in st.session_state.data_store["A"]:
                    matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == record['Subject']]
                    if matches:
                        best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                        status = "BEST PERFORMER" if record['Predictive Score'] >= 60 else "NEEDS IMPROVEMENT"
                        st.session_state.data_store["C"].append({
                            "Class": record['Class'], "Subject": record['Subject'],
                            "Teacher": best_t['Name'], "Current Score": record['Predictive Score'],
                            "Status": status
                        })
                st.success("Auto-Allocation Completed for all records!")
                st.rerun()

        with col_btn2:
            if st.button("🗑️ Reset All Mappings"):
                st.session_state.data_store["C"] = []
                st.rerun()

        if st.session_state.data_store["C"]:
            mapping_df = pd.DataFrame(st.session_state.data_store["C"]).sort_values(by="Class")
            
            # --- Automated Reports Logic ---
            imp_data = mapping_df[mapping_df['Status'] == "NEEDS IMPROVEMENT"].to_dict('records')
            best_data = mapping_df[mapping_df['Status'] == "BEST PERFORMER"].to_dict('records')

            st.divider()
            st.subheader("📥 Download Generated PDF Reports")
            c1, c2 = st.columns(2)
            
            with c1:
                if imp_data:
                    pdf_imp = create_pdf(imp_data, "Improvement Required List")
                    st.download_button("🔴 Download Improvement Report", pdf_imp, "Improvement_Report.pdf")
                else: st.info("No Improvement records.")

            with c2:
                if best_data:
                    pdf_best = create_pdf(best_data, "Best Performers List")
                    st.download_button("🟢 Download Best Performers Report", pdf_best, "Best_Performers_Report.pdf")
                else: st.info("No Best Performer records.")

            st.divider()
            st.write("### Review All Allocations")
            st.dataframe(mapping_df, use_container_width=True)
