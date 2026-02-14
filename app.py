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
    # Weightage: A=100%, B=75%, C=50%, D=25%
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
    df = pd.DataFrame(data).fillna('')
    
    if "Institution" in df.columns:
        df["Institution"] = st.session_state.data_store.get("School_Name", "Global International Academy")

    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 10, f"DOCUMENT SECTION: {title.upper()}", 0, 1, 'L')
    pdf.set_draw_color(31, 73, 125)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    if not df.empty:
        column_widths = {"Institution": 55, "Class": 25, "Subject": 20, "Teacher": 30, "Current Score": 30, "Status": 30}
        default_w = 190 / len(df.columns)

        pdf.set_font('Arial', 'B', 8)
        pdf.set_fill_color(230, 235, 245)
        for col in df.columns:
            w = column_widths.get(col, default_w)
            pdf.cell(w, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 8)
        fill = False
        for _, row in df.iterrows():
            pdf.set_fill_color(248, 248, 248) if fill else pdf.set_fill_color(255, 255, 255)
            for col in df.columns:
                val = str(row[col]) if pd.notnull(row[col]) and str(row[col]) != 'None' else ""
                w = column_widths.get(col, default_w)
                pdf.cell(w, 9, val, 1, 0, 'C', fill=True)
            pdf.ln()
            fill = not fill
            
    return pdf.output(dest='S').encode('latin-1')

# --- 3. BULK UPLOAD LOGIC (MULTI-FILE SYNC) ---
def handle_bulk_upload():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Bulk Data Import Center")
    
    # Live Status Trackers
    s1 = "✅" if st.session_state.data_store["Grades_Config"] else "❌"
    s2 = "✅" if st.session_state.data_store["A"] else "❌"
    s3 = "✅" if st.session_state.data_store["B"] else "❌"
    
    st.sidebar.info(f"Status: Classes {s1} | Students {s2} | Teachers {s3}")

    # File 1: Classes
    up1 = st.sidebar.file_uploader("1. Classes Excel", type=["xlsx"], key="up_cls")
    if up1 and st.sidebar.button("Import Classes"):
        try:
            df = pd.read_excel(up1).fillna('')
            for _, row in df.iterrows():
                key = f"{row['Grade']}-{row['Section']}"
                st.session_state.data_store["Grades_Config"][key] = [s.strip() for s in str(row['Subjects']).split(",")]
            st.sidebar.success("Classes Loaded!")
            st.rerun()
        except Exception as e: st.sidebar.error(f"Error: {e}")

    # File 2: Student Performance
    up2 = st.sidebar.file_uploader("2. Student Performance Excel", type=["xlsx"], key="up_perf")
    if up2 and st.sidebar.button("Import Performance"):
        try:
            df = pd.read_excel(up2).fillna('')
            for col in ['A', 'B', 'C', 'D']: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            for _, row in df.iterrows():
                p_score = calculate_predictive_score(int(row['A']), int(row['B']), int(row['C']), int(row['D']))
                st.session_state.data_store["A"].append({
                    "Class": str(row['Class']), "Subject": str(row['Subject']),
                    "A": int(row['A']), "B": int(row['B']), "C": int(row['C']), "D": int(row['D']),
                    "Total": int(row['A']+row['B']+row['C']+row['D']),
                    "Predictive Score": p_score # 5th Point Requirement
                })
            st.sidebar.success("Performance Loaded!")
            st.rerun()
        except Exception as e: st.sidebar.error(f"Error: {e}")

    # File 3: Teacher Experts
    up3 = st.sidebar.file_uploader("3. Teacher Experts Excel", type=["xlsx"], key="up_teach")
    if up3 and st.sidebar.button("Import Teachers"):
        try:
            df = pd.read_excel(up3).fillna('')
            for _, row in df.iterrows():
                st.session_state.data_store["B"].append({"Name": row['Name'], "Expertise": row['Expertise'], "Success": row['Success']})
            st.sidebar.success("Teachers Loaded!")
            st.rerun()
        except Exception as e: st.sidebar.error(f"Error: {e}")

    if st.sidebar.button("🧹 Reset All Data"):
        st.session_state.data_store = {"Grades_Config": {}, "A": [], "B": [], "C": [], "School_Name": "Global International Academy"}
        st.rerun()

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
    
    if st.session_state.data_store["Grades_Config"]:
        if st.button("🚀 Enter Dashboard"):
            st.session_state.setup_complete = True
            st.rerun()
    else:
        st.warning("Please upload the 'Classes' Excel file in the sidebar to continue.")

else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    display_key = None
    if nav == "Student Performance (A)":
        st.header("📊 Performance Records")
        display_key = "A"
    
    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Faculty Specialization")
        display_key = "B"

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Strategic Deployment")
        display_key = "C"
        if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
            options = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
            sel = st.selectbox("Analyze Needs", options)
            parts = sel.split(" | ")
            class_data = next((x for x in st.session_state.data_store["A"] if x['Class'] == parts[0] and x['Subject'] == parts[1]), None)
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == parts[1]]
            
            if matches and class_data:
                best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                col1, col2 = st.columns(2)
                col1.metric("Current Score", f"{class_data['Predictive Score']}%")
                col2.metric("Target (Teacher)", f"{best_t['Success']}%")
                
                if st.button("Authorize Allocation"):
                    st.session_state.data_store["C"].append({
                        "Institution": st.session_state.data_store["School_Name"],
                        "Class": parts[0], "Subject": parts[1], "Teacher": best_t['Name'],
                        "Current Score": class_data['Predictive Score'], "Status": "DEPLOYED"
                    })
                    st.success("Deployed!")
                    st.rerun()

    if display_key and st.session_state.data_store[display_key]:
        st.divider()
        df_view = pd.DataFrame(st.session_state.data_store[display_key]).fillna('')
        st.dataframe(df_view, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            row_idx = st.selectbox("Select row to delete", df_view.index)
            if st.button("🗑️ Remove Record"):
                st.session_state.data_store[display_key].pop(row_idx)
                st.rerun()
        with c2:
            pdf_bytes = create_pdf(st.session_state.data_store[display_key], nav)
            st.download_button(f"📥 Download {nav} PDF", pdf_bytes, f"Report_{nav}.pdf")
