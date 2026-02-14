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
        "School_Name": ""
    }

# --- 2. PROFESSIONAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        # Prevent "None" in Header
        s_name = st.session_state.data_store.get("School_Name", "")
        school_display = s_name.upper() if s_name else "EDUCATIONAL INSTITUTION"
        self.cell(0, 12, school_display, 0, 1, 'C')
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

def create_pdf(data_list, title):
    pdf = SchoolPDF()
    pdf.add_page()
    # Clean data before PDF generation
    df = pd.DataFrame(data_list).fillna('')
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 10, f"SECTION: {title.upper()}", 0, 1, 'L')
    pdf.ln(5)
    
    if not df.empty:
        pdf.set_font('Arial', 'B', 9)
        col_width = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), 1, 0, 'C')
        pdf.ln()
        
        pdf.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            for val in row:
                text = str(val) if val is not None else ""
                pdf.cell(col_width, 9, text, 1, 0, 'C')
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. BULK UPLOAD LOGIC ---
def handle_bulk_upload():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Data Import")
    upload_type = st.sidebar.selectbox("Category", ["Classes", "Student Performance", "Teachers"], key="upload_sel")
    uploaded_file = st.sidebar.file_uploader(f"Excel File", type=["xlsx"], key="file_up")

    if uploaded_file is not None:
        if st.sidebar.button(f"Import {upload_type}"):
            try:
                # Use fillna('') to kill the "None" strings at the source
                df = pd.read_excel(uploaded_file).fillna('')
                if upload_type == "Classes":
                    for _, row in df.iterrows():
                        key = f"{row['Grade']}-{row['Section']}"
                        st.session_state.data_store["Grades_Config"][key] = [s.strip() for s in str(row['Subjects']).split(",")]
                elif upload_type == "Student Performance":
                    for _, row in df.iterrows():
                        st.session_state.data_store["A"].append({
                            "Class": row.get('Class', ''), "Subject": row.get('Subject', ''),
                            "A": row.get('A', 0), "B": row.get('B', 0), "C": row.get('C', 0), "D": row.get('D', 0)
                        })
                st.sidebar.success("Success!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

# --- 4. MAIN UI ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Login")
    if st.text_input("Key", type="password") == ACTIVATION_KEY:
        if st.button("Login"):
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    st.title("🏫 Setup")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "Global Academy")
    if st.button("Initialize Dashboard"):
        st.session_state.setup_complete = True
        st.rerun()

else:
    st.title(f"🏢 {st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Menu", ["Performance", "Teachers", "Mapping"])

    display_key = "A" if nav == "Performance" else "B" if nav == "Teachers" else "C"
    
    # Display the table
    if st.session_state.data_store[display_key]:
        df_view = pd.DataFrame(st.session_state.data_store[display_key]).fillna('')
        st.table(df_view) # Use st.table for cleaner look without "None" headers
        
        # FIXED: Row Deletion and PDF Section
        col1, col2 = st.columns(2)
        with col1:
            # Use index numbers 0, 1, 2... instead of labels to avoid "None"
            row_to_del = st.number_input("Enter Row Index to Delete", min_value=0, max_value=len(df_view)-1, step=1)
            if st.button("🗑️ Delete Row"):
                st.session_state.data_store[display_key].pop(int(row_to_del))
                st.rerun()
        
        with col2:
            pdf_data = create_pdf(st.session_state.data_store[display_key], nav)
            st.download_button("📄 Download PDF", pdf_data, f"{nav}.pdf")
    else:
        st.info("No data available in this section.")
