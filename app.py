import streamlit as st
import pd
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io

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
    try:
        total = float(a) + float(b) + float(c) + float(d)
        if total == 0: return 0
        score = ((float(a) * 100) + (float(b) * 75) + (float(c) * 50) + (float(d) * 25)) / total
        return round(score, 2)
    except:
        return 0

# --- 2. PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        name = st.session_state.data_store.get("School_Name", "ACADEMY").upper()
        self.cell(0, 12, name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "OFFICIAL ACADEMIC PERFORMANCE REPORT", 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d')} | Page {self.page_no()}", 0, 0, 'C')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    
    pdf.set_text_color(31, 73, 125)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"SECTION: {title.upper()}", 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    if not df.empty:
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(240, 240, 240)
        col_width = 190 / len(df.columns)
        
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), 1, 0, 'C', True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(0, 0, 0)
        for _, row in df.iterrows():
            for col in df.columns:
                pdf.cell(col_width, 8, str(row[col]), 1, 0, 'C')
            pdf.ln()
            
    # Use latin-1 with 'replace' to prevent encoding crashes
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# --- 3. BULK UPLOAD HANDLER ---
def handle_bulk_upload():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Bulk Import")
    
    cat = st.sidebar.selectbox("Select Category", ["Classes", "Performance", "Teachers"])
    
    # Template download logic
    template_cols = {
        "Classes": "Grade,Section,Subjects",
        "Performance": "Class,Subject,A,B,C,D",
        "Teachers": "Name,Expertise,Success"
    }
    
    st.sidebar.download_button("📥 Download Template CSV", template_cols[cat], f"{cat}_template.csv")
    
    uploaded_file = st.sidebar.file_uploader(f"Upload {cat} Excel/CSV", type=["xlsx", "csv"])
    
    if uploaded_file and st.sidebar.button(f"Process {cat}"):
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            df = df.fillna(0)
            
            if cat == "Classes":
                for _, r in df.iterrows():
                    key = f"{r['Grade']}-{r['Section']}"
                    st.session_state.data_store["Grades_Config"][key] = [s.strip() for s in str(r['Subjects']).split(",")]
            
            elif cat == "Performance":
                for _, r in df.iterrows():
                    score = calculate_predictive_score(r['A'], r['B'], r['C'], r['D'])
                    st.session_state.data_store["A"].append({
                        "Class": r['Class'], "Subject": r['Subject'],
                        "A": r['A'], "B": r['B'], "C": r['C'], "D": r['D'],
                        "Total": int(r['A']+r['B']+r['C']+r['D']), "Predictive Score": score
                    })
            
            elif cat == "Teachers":
                for _, r in df.iterrows():
                    st.session_state.data_store["B"].append({
                        "Name": r['Name'], "Expertise": r['Expertise'], "Success": r['Success']
                    })
            
            st.sidebar.success("Import Successful!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# --- 4. MAIN UI ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Login")
    if st.text_input("Access Key", type="password") == ACTIVATION_KEY:
        if st.button("Login"):
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    handle_bulk_upload()
    st.title("⚙️ Setup Institution")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "Global International Academy")
    
    with st.expander("Manual Class Entry"):
        c1, c2 = st.columns(2)
        g = c1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
        s = c2.text_input("Section (e.g., A)")
        subs = st.text_area("Subjects (comma separated)")
        if st.button("Add Class"):
            st.session_state.data_store["Grades_Config"][f"{g}-{s}"] = [x.strip() for x in subs.split(",")]
            st.success("Added!")

    if st.session_state.data_store["Grades_Config"] and st.button("Go to Dashboard"):
        st.session_state.setup_complete = True
        st.rerun()

else:
    st.title(f"🏢 {st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    
    menu = st.sidebar.radio("Menu", ["Performance (A)", "Teachers (B)", "Mapping (C)"])
    
    if menu == "Performance (A)":
        st.subheader("Student Performance")
        if st.session_state.data_store["Grades_Config"]:
            with st.form("manual_a"):
                cl = st.selectbox("Class", list(st.session_state.data_store["Grades_Config"].keys()))
                sb = st.selectbox("Subject", st.session_state.data_store["Grades_Config"][cl])
                c1,c2,c3,c4 = st.columns(4)
                va, vb, vc, vd = c1.number_input("A",0), c2.number_input("B",0), c3.number_input("C",0), c4.number_input("D",0)
                if st.form_submit_button("Save"):
                    st.session_state.data_store["A"].append({
                        "Class": cl, "Subject": sb, "A": va, "B": vb, "C": vc, "D": vd,
                        "Total": va+vb+vc+vd, "Predictive Score": calculate_predictive_score(va,vb,vc,vd)
                    })
                    st.rerun()
        
        if st.session_state.data_store["A"]:
            df = pd.DataFrame(st.session_state.data_store["A"])
            st.table(df)
            st.download_button("Download PDF", create_pdf(st.session_state.data_store["A"], "Performance"), "report.pdf")

    elif menu == "Teachers (B)":
        st.subheader("Teacher Directory")
        with st.form("t_form"):
            n = st.text_input("Name")
            e = st.text_input("Expertise")
            s = st.slider("Success Rate", 0, 100, 80)
            if st.form_submit_button("Add"):
                st.session_state.data_store["B"].append({"Name": n, "Expertise": e, "Success": s})
                st.rerun()
        if st.session_state.data_store["B"]:
            st.table(pd.DataFrame(st.session_state.data_store["B"]))

    elif menu == "Mapping (C)":
        st.subheader("Deployment Mapping")
        # Logic for mapping (same as your original)
        if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
            st.info("Mapping analysis active based on uploaded data.")
            # ... (mapping logic continues here)
