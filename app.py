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
        school_name = st.session_state.data_store.get("School_Name", "EDUCATIONAL INSTITUTION").upper()
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

def create_pdf(data_list, title):
    pdf = SchoolPDF()
    pdf.add_page()
    
    # Convert list of dicts to DataFrame and clean up
    df = pd.DataFrame(data_list).fillna('')
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 10, f"DOCUMENT SECTION: {title.upper()}", 0, 1, 'L')
    pdf.set_draw_color(31, 73, 125)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    if not df.empty:
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(230, 235, 245)
        col_width = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 8)
        fill = False
        for _, row in df.iterrows():
            pdf.set_fill_color(248, 248, 248) if fill else pdf.set_fill_color(255, 255, 255)
            for val in row:
                # Ensure we don't try to print 'None' or non-latin chars
                text = str(val).encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(col_width, 9, text, 1, 0, 'C', fill=True)
            pdf.ln()
            fill = not fill
    return pdf.output(dest='S').encode('latin-1')

# --- 3. BULK UPLOAD LOGIC ---
def handle_bulk_upload():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Excel Data Import")
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
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    for _, row in df.iterrows():
                        total = int(row.get('A',0)+row.get('B',0)+row.get('C',0)+row.get('D',0))
                        st.session_state.data_store["A"].append({
                            "Class": str(row.get('Class','')), "Subject": str(row.get('Subject','')),
                            "A": int(row.get('A',0)), "B": int(row.get('B',0)), 
                            "C": int(row.get('C',0)), "D": int(row.get('D',0)),
                            "Total": total
                        })
                elif upload_type == "Teachers":
                    for _, row in df.iterrows():
                        st.session_state.data_store["B"].append({
                            "Name": str(row.get('Name','')), 
                            "Expertise": str(row.get('Expertise','')), 
                            "Success": row.get('Success', 0)
                        })
                st.sidebar.success("Data Imported!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

# --- 4. NAVIGATION & UI ---
if not st.session_state.authenticated:
    st.title("Secure Access")
    key_input = st.text_input("Enter System Key", type="password")
    if st.button("Authenticate"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Invalid Key")

elif not st.session_state.setup_complete:
    handle_bulk_upload()
    st.title("Institution Setup")
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
        if st.button("Enter Dashboard"):
            st.session_state.setup_complete = True
            st.rerun()

else:
    st.title(f"{st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    display_key = None
    if nav == "Student Performance (A)":
        st.header("Performance Records")
        display_key = "A"
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        if class_list:
            with st.expander("Manual Entry"):
                sel_class = st.selectbox("Class", class_list)
                sel_sub = st.selectbox("Subject", st.session_state.data_store["Grades_Config"][sel_class])
                with st.form("a_form"):
                    c1,c2,c3,c4 = st.columns(4)
                    ga,gb,gc,gd = c1.number_input("A",0), c2.number_input("B",0), c3.number_input("C",0), c4.number_input("D",0)
                    if st.form_submit_button("Save Record"):
                        st.session_state.data_store["A"].append({"Class": sel_class, "Subject": sel_sub, "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd})
                        st.rerun()

    elif nav == "Teacher Experts (B)":
        st.header("Faculty Specialization")
        display_key = "B"
        all_subs = set()
        for s_list in st.session_state.data_store["Grades_Config"].values(): all_subs.update(s_list)
        with st.form("b_form"):
            t_name = st.text_input("Teacher Name")
            t_exp = st.selectbox("Expertise", list(all_subs) if all_subs else ["N/A"])
            t_rate = st.slider("Success %", 0, 100, 80)
            if st.form_submit_button("Register Teacher"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_rate})
                st.rerun()

    elif nav == "Efficiency Mapping (C)":
        st.header("Strategic Deployment")
        display_key = "C"
        if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
            options = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
            sel = st.selectbox("Analyze Needs", options)
            parts = sel.split(" | ")
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == parts[1]]
            if matches:
                best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                st.info(f"Recommended Faculty: {best_t['Name']}")
                if st.button("Authorize Allocation"):
                    st.session_state.data_store["C"].append({
                        "Institution": st.session_state.data_store["School_Name"],
                        "Class": parts[0], "Subject": parts[1],
                        "Teacher": best_t['Name'], "Status": "DEPLOYED"
                    })
                    st.rerun()

    # --- UPDATED DATA VIEW & EXPORT ---
    if display_key and st.session_state.data_store[display_key]:
        st.divider()
        st.subheader(f"Data Management: {nav}")
        df_view = pd.DataFrame(st.session_state.data_store[display_key]).fillna('')
        st.dataframe(df_view, use_container_width=True)
        
        col_del, col_pdf = st.columns([1, 1])
        
        with col_del:
            # Clean deletion UI
            row_idx = st.number_input("Row index to delete", min_value=0, max_value=len(df_view)-1, step=1)
            if st.button("Delete Selected Row", type="secondary"):
                st.session_state.data_store[display_key].pop(int(row_idx))
                st.rerun()
                
        with col_pdf:
            # Safe PDF Generation
            try:
                pdf_bytes = create_pdf(st.session_state.data_store[display_key], nav)
                st.download_button(
                    label="Download Official PDF",
                    data=pdf_bytes,
                    file_name=f"Report_{nav.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF Error: {e}")
