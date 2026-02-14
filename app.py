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
        school_name = str(st.session_state.data_store.get("School_Name", "EDUCATIONAL INSTITUTION")).upper()
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

def clean_text(val):
    """Deep cleaning helper to stop 'None' or 'nan' from appearing"""
    if pd.isna(val) or val is None or str(val).lower() in ['nan', 'none', '']:
        return ""
    return str(val)

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
                pdf.cell(col_width, 9, clean_text(val), 1, 0, 'C', fill=True)
            pdf.ln()
            fill = not fill
    return pdf.output(dest='S').encode('latin-1')

# --- 3. BULK UPLOAD LOGIC ---
def handle_bulk_upload():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Excel Data Import")
    u_type = st.sidebar.selectbox("Category", ["Classes", "Student Performance", "Teachers"], key="bulk_cat")
    u_file = st.sidebar.file_uploader(f"Upload {u_type}", type=["xlsx"], key="bulk_file")

    if u_file and st.sidebar.button(f"Process {u_type}"):
        try:
            # Drop completely empty rows and fill remaining NaN with empty string
            df = pd.read_excel(u_file).dropna(how='all').fillna('')
            df.columns = [str(c).strip() for c in df.columns]
            
            if u_type == "Classes":
                for _, row in df.iterrows():
                    g, s = clean_text(row.get('Grade')), clean_text(row.get('Section'))
                    if g and s:
                        key = f"{g}-{s}"
                        subs = [sub.strip() for sub in str(row.get('Subjects', '')).split(",") if sub.strip()]
                        st.session_state.data_store["Grades_Config"][key] = subs
            
            elif u_type == "Student Performance":
                for _, row in df.iterrows():
                    cls = clean_text(row.get('Class'))
                    if cls: # Only add if the class name isn't empty
                        st.session_state.data_store["A"].append({
                            "Class": cls, "Subject": clean_text(row.get('Subject')),
                            "A": int(row['A']) if str(row['A']).isdigit() else 0,
                            "B": int(row['B']) if str(row['B']).isdigit() else 0,
                            "C": int(row['C']) if str(row['C']).isdigit() else 0,
                            "D": int(row['D']) if str(row['D']).isdigit() else 0,
                            "Total": 0 
                        })
                        last = st.session_state.data_store["A"][-1]
                        last["Total"] = last["A"] + last["B"] + last["C"] + last["D"]

            elif u_type == "Teachers":
                for _, row in df.iterrows():
                    name = clean_text(row.get('Name'))
                    if name:
                        st.session_state.data_store["B"].append({
                            "Name": name, 
                            "Expertise": clean_text(row.get('Expertise')), 
                            "Success": row['Success'] if row['Success'] != '' else 0
                        })
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Import Failed: {e}")

# --- 4. MAIN UI ---
if not st.session_state.authenticated:
    st.title("🔐 Secure System Activation")
    pwd = st.text_input("Activation Key", type="password")
    if st.button("Unlock"):
        if pwd == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Access Denied")

elif not st.session_state.setup_complete:
    st.title("⚙️ Initial Setup")
    handle_bulk_upload()
    st.session_state.data_store["School_Name"] = st.text_input("Official School Name", "My Academy")
    
    with st.expander("Add Classes Manually"):
        c1, c2 = st.columns(2)
        g = c1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
        s = c2.text_input("Section (e.g. A)")
        subs = st.text_area("Subjects (comma separated)")
        if st.button("Add Class"):
            if s:
                st.session_state.data_store["Grades_Config"][f"{g}-{s}"] = [x.strip() for x in subs.split(",") if x.strip()]
    
    if st.session_state.data_store["Grades_Config"]:
        if st.button("🚀 Launch System"):
            st.session_state.setup_complete = True
            st.rerun()

else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Navigation", ["Section A: Students", "Section B: Teachers", "Section C: Strategy"])

    d_key = "A" if "Students" in nav else "B" if "Teachers" in nav else "C"
    
    if d_key == "A":
        st.header("📊 Student Performance")
        classes = list(st.session_state.data_store["Grades_Config"].keys())
        if classes:
            with st.form("add_a"):
                sel_c = st.selectbox("Class", classes)
                sel_s = st.selectbox("Subject", st.session_state.data_store["Grades_Config"][sel_c])
                col1, col2, col3, col4 = st.columns(4)
                vA, vB, vC, vD = col1.number_input("A", 0), col2.number_input("B", 0), col3.number_input("C", 0), col4.number_input("D", 0)
                if st.form_submit_button("Add Record"):
                    st.session_state.data_store["A"].append({
                        "Class": sel_c, "Subject": sel_s, "A": vA, "B": vB, "C": vC, "D": vD, "Total": vA+vB+vC+vD
                    })
                    st.rerun()

    elif d_key == "B":
        st.header("👨‍🏫 Teacher Specialization")
        with st.form("add_b"):
            t_name = st.text_input("Teacher Name")
            t_exp = st.text_input("Expertise (Subject)")
            t_suc = st.slider("Success Rate %", 0, 100, 85)
            if st.form_submit_button("Register Teacher"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_suc})
                st.rerun()

    elif d_key == "C":
        st.header("🎯 Strategy Mapping")
        if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
            analysis_opts = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
            target = st.selectbox("Select Target", analysis_opts)
            if st.button("Generate Strategy"):
                sub = target.split(" | ")[1]
                matches = [t for t in st.session_state.data_store["B"] if t['Expertise'].lower() == sub.lower()]
                best = sorted(matches, key=lambda x: x['Success'], reverse=True)[0] if matches else None
                st.session_state.data_store["C"].append({
                    "Target": target,
                    "Assigned": best['Name'] if best else "Unassigned",
                    "Success_Score": best['Success'] if best else 0,
                    "Status": "Verified"
                })
                st.rerun()

    if st.session_state.data_store[d_key]:
        st.divider()
        current_df = pd.DataFrame(st.session_state.data_store[d_key])
        st.dataframe(current_df, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            idx = st.number_input("Row index to delete", 0, max(0, len(current_df)-1), 0)
            if st.button("Delete Selected Row") and len(current_df) > 0:
                st.session_state.data_store[d_key].pop(idx)
                st.rerun()
        with c2:
            pdf_data = create_pdf(st.session_state.data_store[d_key], nav)
            st.download_button("📥 Download Official PDF", pdf_data, f"{nav}_Report.pdf")
