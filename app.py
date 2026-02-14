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
        # Header Box
        self.set_fill_color(41, 128, 185)  # Professional Blue
        self.rect(0, 0, 210, 40, 'F')
       
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        school_name = st.session_state.data_store.get("School_Name", "INSTITUTION REPORT").upper()
        self.cell(0, 15, school_name, 0, 1, 'C')
       
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, "Confidential Academic Performance Document", 0, 1, 'C')
        self.set_text_color(0, 0, 0) # Reset
        self.ln(20)

    def footer(self):
        self.set_y(-30)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        # Signature Line
        self.cell(0, 10, "__________________________", 0, 1, 'R')
        self.cell(0, 5, "Authorized Signature & Stamp", 0, 1, 'R')
       
        self.cell(0, 10, f"Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Page {self.page_no()}", 0, 0, 'L')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
   
    # Report Sub-Header
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 10, f"REPORT TYPE: {title.upper()}", 0, 1, 'L')
    pdf.set_draw_color(41, 128, 185)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
   
    # Table Styling
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(0, 0, 0)
   
    if not df.empty:
        col_width = 190 / len(df.columns)
        # Header Row
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
       
        # Data Rows with Zebra Striping
        pdf.set_font('Arial', '', 9)
        fill = False
        for _, row in df.iterrows():
            pdf.set_fill_color(248, 249, 249) if fill else pdf.set_fill_color(255, 255, 255)
            for val in row:
                pdf.cell(col_width, 9, str(val), 1, 0, 'C', fill=True)
            pdf.ln()
            fill = not fill
           
    return pdf.output(dest='S').encode('latin-1')

# --- 3. BULK UPLOAD LOGIC ---
def handle_bulk_upload():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Excel Bulk Load")
    upload_type = st.sidebar.selectbox("Select Upload Type", ["Classes", "Student Performance", "Teachers"])
    uploaded_file = st.sidebar.file_uploader(f"Upload {upload_type} Excel", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip() for c in df.columns]
            if st.sidebar.button(f"Process {upload_type}"):
                if upload_type == "Classes":
                    for _, row in df.iterrows():
                        key = f"{row['Grade']}-{row['Section']}"
                        subs = [s.strip() for s in str(row['Subjects']).split(",")]
                        st.session_state.data_store["Grades_Config"][key] = subs
                elif upload_type == "Student Performance":
                    for col in ['A', 'B', 'C', 'D']:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    for _, row in df.iterrows():
                        st.session_state.data_store["A"].append({
                            "Class": str(row['Class']), "Subject": str(row['Subject']),
                            "A": int(row['A']), "B": int(row['B']), "C": int(row['C']), "D": int(row['D']),
                            "Total": int(row['A']+row['B']+row['C']+row['D'])
                        })
                elif upload_type == "Teachers":
                    for _, row in df.iterrows():
                        st.session_state.data_store["B"].append({
                            "Name": row['Name'], "Expertise": row['Expertise'], "Success": row['Success']
                        })
                st.rerun()
        except: st.sidebar.error("Upload Error.")

# --- 4. UI LOGIC ---
if not st.session_state.authenticated:
    st.title("🔐 System Activation")
    key_input = st.text_input("Enter Key", type="password")
    if st.button("Activate"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    handle_bulk_upload()
    st.title("⚙️ Institution Setup")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "Global Academy")
   
    st.subheader("Class Setup")
    c1, c2 = st.columns(2)
    g_name = c1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
    s_name = c2.text_input("Section")
    sub_input = st.text_area("Subjects (comma separated)", "Math, Science")
   
    if st.button("Add Class"):
        if s_name:
            full_key = f"{g_name}-{s_name}"
            subjects = [s.strip() for s in sub_input.split(",") if s.strip()]
            st.session_state.data_store["Grades_Config"][full_key] = subjects
            st.success("Class Added")
   
    if st.session_state.data_store["Grades_Config"]:
        if st.button("🚀 Launch Dashboard"):
            st.session_state.setup_complete = True
            st.rerun()

else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Navigation", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    display_key = None

    if nav == "Student Performance (A)":
        st.header("📊 Student Performance")
        display_key = "A"
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        if class_list:
            with st.expander("Add Entry"):
                sel_class = st.selectbox("Class", class_list)
                sel_sub = st.selectbox("Subject", st.session_state.data_store["Grades_Config"][sel_class])
                with st.form("a"):
                    c1,c2,c3,c4 = st.columns(4)
                    ga,gb,gc,gd = c1.number_input("A",0), c2.number_input("B",0), c3.number_input("C",0), c4.number_input("D",0)
                    if st.form_submit_button("Save"):
                        st.session_state.data_store["A"].append({"Class": sel_class, "Subject": sel_sub, "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd})
                        st.rerun()

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Faculty Specialization")
        display_key = "B"
        all_subs = set()
        for s_list in st.session_state.data_store["Grades_Config"].values(): all_subs.update(s_list)
        with st.form("b"):
            t_name = st.text_input("Name")
            t_exp = st.selectbox("Expertise", list(all_subs) if all_subs else ["N/A"])
            t_rate = st.slider("Success %", 0, 100, 80)
            if st.form_submit_button("Register"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_rate})
                st.rerun()

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Deployment Strategy")
        display_key = "C"
        if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
            options = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
            sel = st.selectbox("Analyze", options)
            parts = sel.split(" | ")
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == parts[1]]
            if matches:
                best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                st.info(f"Recommended: {best_t['Name']}")
                if st.button("Confirm"):
                    st.session_state.data_store["C"].append({
                        "Class": parts[0], "Subject": parts[1],
                        "Teacher": best_t['Name'], "Status": "Authorized"
                    })
                    st.rerun()

    if display_key and st.session_state.data_store[display_key]:
        st.divider()
        st.subheader(f"📋 Records Table: {nav}")
        df_view = pd.DataFrame(st.session_state.data_store[display_key])
        st.dataframe(df_view, use_container_width=True)
       
        c1, c2 = st.columns(2)
        with c1:
            row_to_del = st.selectbox("Delete Row", df_view.index)
            if st.button("🗑️ Remove"):
                st.session_state.data_store[display_key].pop(row_to_del)
                st.rerun()
        with c2:
            pdf_bytes = create_pdf(st.session_state.data_store[display_key], nav)
            st.download_button(f"📥 Download Official {nav} PDF",
                               pdf_bytes, f"Official_Report_{nav}.pdf")
