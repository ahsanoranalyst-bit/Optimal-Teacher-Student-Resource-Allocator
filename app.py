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
        # Professional Header Banner
        self.set_fill_color(31, 73, 125)  # Navy Blue
        self.rect(0, 0, 210, 35, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 20)
        school_name = st.session_state.data_store.get("School_Name", "INSTITUTION").upper()
        self.cell(0, 10, school_name, 0, 1, 'C')
        
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, "OFFICIAL ACADEMIC EFFICIENCY & DEPLOYMENT REPORT", 0, 1, 'C')
        self.set_text_color(0, 0, 0) # Reset text color
        self.ln(15)

    def footer(self):
        self.set_y(-30)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        
        # Signature Block
        self.cell(0, 10, "Authorized Signature: __________________________", 0, 1, 'R')
        self.cell(0, 5, "Official School Stamp Required", 0, 1, 'R')
        
        self.ln(5)
        curr_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cell(0, 10, f"System Record ID: {ACTIVATION_KEY} | Generated: {curr_time} | Page {self.page_no()}", 0, 0, 'L')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    
    # Section Header
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 10, f"DATA SECTION: {title.upper()}", 0, 1, 'L')
    pdf.set_draw_color(31, 73, 125)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Table Styling
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(220, 230, 241) # Light blue header
    pdf.set_text_color(0, 0, 0)
    
    if not df.empty:
        # Calculate dynamic column width
        col_width = 190 / len(df.columns)
        
        # Draw Headers
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        
        # Draw Data Rows (Zebra Striping)
        pdf.set_font('Arial', '', 8)
        fill = False
        for _, row in df.iterrows():
            pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
            for val in row:
                pdf.cell(col_width, 9, str(val), 1, 0, 'C', fill=True)
            pdf.ln()
            fill = not fill
            
    return pdf.output(dest='S').encode('latin-1')

# --- 3. BULK UPLOAD LOGIC ---
def handle_bulk_upload():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Bulk Data Upload")
    upload_type = st.sidebar.selectbox("Category", ["Classes", "Performance", "Teachers"])
    uploaded_file = st.sidebar.file_uploader(f"Choose {upload_type} Excel", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip() for c in df.columns]
            if st.sidebar.button(f"Confirm {upload_type} Import"):
                if upload_type == "Classes":
                    for _, row in df.iterrows():
                        key = f"{row['Grade']}-{row['Section']}"
                        subs = [s.strip() for s in str(row['Subjects']).split(",")]
                        st.session_state.data_store["Grades_Config"][key] = subs
                elif upload_type == "Performance":
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
                st.sidebar.success("Import Successful!")
                st.rerun()
        except: st.sidebar.error("Invalid File Format.")

# --- 4. MAIN INTERFACE ---
if not st.session_state.authenticated:
    st.title("🛡️ System Authentication")
    key_input = st.text_input("Enter Activation Key", type="password")
    if st.button("Access Dashboard"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    st.title("⚙️ Institution Configuration")
    st.session_state.data_store["School_Name"] = st.text_input("Enter Full Institution Name", "Global International School")
    
    st.subheader("Manual Class Setup")
    c1, c2 = st.columns(2)
    g_name = c1.selectbox("Grade Level", [f"Grade {i}" for i in range(1, 13)])
    s_name = c2.text_input("Section Code")
    sub_input = st.text_area("Subjects (Comma separated list)", "Mathematics, Science, English")
    
    if st.button("Add Class Structure"):
        if s_name:
            full_key = f"{g_name}-{s_name}"
            subjects = [s.strip() for s in sub_input.split(",") if s.strip()]
            st.session_state.data_store["Grades_Config"][full_key] = subjects
            st.success("Structure Updated.")
    
    if st.session_state.data_store["Grades_Config"]:
        if st.button("✅ Finalize Setup"):
            st.session_state.setup_complete = True
            st.rerun()

else:
    st.title(f"🏢 {st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Navigation", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    display_key = None

    if nav == "Student Performance (A)":
        st.header("📊 Student Performance Data")
        display_key = "A"
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        if class_list:
            with st.expander("Add Manual Entry"):
                sel_class = st.selectbox("Select Class", class_list)
                sel_sub = st.selectbox("Select Subject", st.session_state.data_store["Grades_Config"][sel_class])
                with st.form("a"):
                    c1,c2,c3,c4 = st.columns(4)
                    ga,gb,gc,gd = c1.number_input("Grade A",0), c2.number_input("Grade B",0), c3.number_input("Grade C",0), c4.number_input("Grade D",0)
                    if st.form_submit_button("Save Performance"):
                        st.session_state.data_store["A"].append({"Class": sel_class, "Subject": sel_sub, "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd})
                        st.rerun()

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Faculty Expertise")
        display_key = "B"
        all_subs = set()
        for s_list in st.session_state.data_store["Grades_Config"].values(): all_subs.update(s_list)
        with st.form("b"):
            t_name = st.text_input("Faculty Full Name")
            t_exp = st.selectbox("Specialization", list(all_subs) if all_subs else ["N/A"])
            t_rate = st.slider("Success Rating (%)", 0, 100, 85)
            if st.form_submit_button("Register Faculty"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_rate})
                st.rerun()

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Professional Deployment Strategy")
        display_key = "C"
        if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
            options = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
            sel = st.selectbox("Analyze Class Need", options)
            parts = sel.split(" | ")
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == parts[1]]
            
            if matches:
                best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                st.info(f"Recommended Expert for {parts[1]}: **{best_t['Name']}**")
                if st.button("Confirm Deployment"):
                    # ADDING THE INSTITUTION NAME HERE FOR SECTION C
                    st.session_state.data_store["C"].append({
                        "Institution": st.session_state.data_store["School_Name"],
                        "Class": parts[0], 
                        "Subject": parts[1],
                        "Assigned Teacher": best_t['Name'], 
                        "Status": "AUTHORIZED"
                    })
                    st.rerun()

    # --- SHARED RECORDS VIEW ---
    if display_key and st.session_state.data_store[display_key]:
        st.divider()
        st.subheader(f"📋 Official Record Table: {nav}")
        df_view = pd.DataFrame(st.session_state.data_store[display_key])
        st.dataframe(df_view, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            row_to_del = st.selectbox("Select Row to Remove", df_view.index)
            if st.button("🗑️ Delete Selected Record"):
                st.session_state.data_store[display_key].pop(row_to_del)
                st.rerun()
        with c2:
            pdf_bytes = create_pdf(st.session_state.data_store[display_key], nav)
            st.download_button(f"📥 Export Official PDF",
                               pdf_bytes, f"Report_{st.session_state.data_store['School_Name']}_{nav}.pdf")
