

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
        self.cell(0, 8, "OFFICIAL PERFORMANCE & ANALYSIS REPORT", 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(15)

    def footer(self):
        self.set_y(-30)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "__________________________", 0, 1, 'R')
        self.cell(0, 5, "Authorized Signature & Stamp", 0, 1, 'R')
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
        pdf.set_font('Arial', 'B', 8)
        pdf.set_fill_color(230, 235, 245)
        w = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(w, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            for col in df.columns:
                val = str(row[col]) if pd.notnull(row[col]) else ""
                pdf.cell(w, 9, val, 1, 0, 'C')
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
                    for col in ['A', 'B', 'C', 'D']:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
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
    if st.button("Authenticate"):
        if st.text_input("Key", type="password") == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()

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
    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)", "Teacher Personal Report"])

    if nav == "Student Performance (A)":
        st.header("📊 Performance Records")
        if st.session_state.data_store["A"]:
            st.dataframe(pd.DataFrame(st.session_state.data_store["A"]))

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Faculty Specialization")
        if st.session_state.data_store["B"]:
            st.dataframe(pd.DataFrame(st.session_state.data_store["B"]))

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Efficiency Mapping & Admin Proofs")
        
        if st.button("🔄 Auto-Map All Classes"):
            st.session_state.data_store["C"] = []
            for record in st.session_state.data_store["A"]:
                matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == record['Subject']]
                if matches:
                    best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                    # Logic: Identify Best vs Improvement for the PDF Status
                    status_label = "BEST TEACHER" if record['Predictive Score'] >= 70 else "IMPROVEMENT NEEDED"
                    st.session_state.data_store["C"].append({
                        "Class": record['Class'], "Subject": record['Subject'], "Teacher": best_t['Name'],
                        "Score": record['Predictive Score'], "Status": status_label
                    })
            st.success("Mapping Complete.")

        if st.session_state.data_store["C"]:
            df_c = pd.DataFrame(st.session_state.data_store["C"])
            best_df = df_c[df_c["Status"] == "BEST TEACHER"]
            improve_df = df_c[df_c["Status"] == "IMPROVEMENT NEEDED"]
            
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"Best List: {len(best_df)}")
                if not best_df.empty:
                    st.download_button("📥 Download Best PDF", create_pdf(best_df, "BEST TEACHER LIST"), "Best_Performers.pdf")
            with c2:
                st.warning(f"Improvement List: {len(improve_df)}")
                if not improve_df.empty:
                    st.download_button("📥 Download Improvement PDF", create_pdf(improve_df, "IMPROVEMENT NEEDED LIST"), "Improvement_List.pdf")
            st.dataframe(df_c)

    elif nav == "Teacher Personal Report":
        st.header("📜 Teacher Performance Portal")
        teachers = list(set([t['Name'] for t in st.session_state.data_store["B"]]))
        selected_t = st.selectbox("Select Teacher", teachers)
        
        # Filter personal data and add performance context
        personal_data = [x for x in st.session_state.data_store["C"] if x['Teacher'] == selected_t]
        
        if personal_data:
            st.write(f"Showing performance summary for: **{selected_t}**")
            st.dataframe(pd.DataFrame(personal_data))
            pdf_report = create_pdf(personal_data, f"PERSONAL PERFORMANCE REPORT: {selected_t}")
            st.download_button(f"📥 Download {selected_t}'s PDF", pdf_report, f"{selected_t}_Performance.pdf")
        else:
            st.info("No mapping data found for this teacher yet.")
