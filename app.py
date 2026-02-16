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
    df = pd.DataFrame(data)
    
    if "Institution" in df.columns:
        df["Institution"] = st.session_state.data_store["School_Name"]

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
                st.sidebar.success("Import Successful!")
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
    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)", "Teacher Personal Report"])

    display_key = None
    if nav == "Student Performance (A)":
        st.header("📊 Performance Records & Prediction")
        display_key = "A"
        # Manual Entry logic (Original restored)
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        if class_list:
            with st.expander("➕ Manual Entry"):
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
                            "Total": ga+gb+gc+gd, "Predictive Score": p_score
                        })
                        st.rerun()

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Faculty Specialization")
        display_key = "B"
        with st.form("b_form"):
            t_name = st.text_input("Teacher Name")
            t_exp = st.text_input("Expertise (Subject)")
            t_rate = st.slider("Success %", 0, 100, 80)
            if st.form_submit_button("Register"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_rate})
                st.rerun()

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Strategic Deployment & Swapping Logic")
        display_key = "C"
        
        # Auto-Mapping Logic
        if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
            if st.button("🔄 Auto-Map All Classes"):
                st.session_state.data_store["C"] = []
                for record in st.session_state.data_store["A"]:
                    matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == record['Subject']]
                    if matches:
                        best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                        st.session_state.data_store["C"].append({
                            "Class": record['Class'], "Subject": record['Subject'], "Teacher": best_t['Name'],
                            "Current Score": record['Predictive Score'], "Status": "AUTO-MAPPED"
                        })
                st.success("Auto-mapping complete.")

        # Manual Deployment logic (Your original)
        if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
            options = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
            sel = st.selectbox("Analyze Needs", options)
            parts = sel.split(" | ")
            class_data = next((x for x in st.session_state.data_store["A"] if x['Class'] == parts[0] and x['Subject'] == parts[1]), None)
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == parts[1]]
            
            if matches and class_data:
                best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                if st.button("Authorize Allocation"):
                    st.session_state.data_store["C"].append({
                        "Class": parts[0], "Subject": parts[1], "Teacher": best_t['Name'],
                        "Current Score": class_data['Predictive Score'], "Status": "DEPLOYED"
                    })
                    st.success("Allocation Authorized.")
                    st.rerun()

        # DUAL PDF DOWNLOADS (Best vs Improvement)
        if st.session_state.data_store["C"]:
            st.divider()
            df_c = pd.DataFrame(st.session_state.data_store["C"])
            best_df = df_c[df_c["Current Score"] >= 70]
            improve_df = df_c[df_c["Current Score"] < 70]
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"Best Teachers ({len(best_df)})")
                if not best_df.empty:
                    st.download_button("📥 Download Best PDF", create_pdf(best_df.to_dict('records'), "BEST TEACHERS"), "Best_Performers.pdf")
            with col2:
                st.warning(f"Improvement Required ({len(improve_df)})")
                if not improve_df.empty:
                    st.download_button("📥 Download Improvement PDF", create_pdf(improve_df.to_dict('records'), "IMPROVEMENT NEEDED"), "Improvement_List.pdf")

    elif nav == "Teacher Personal Report":
        st.header("📜 Teacher Performance Portal")
        teachers = list(set([t['Name'] for t in st.session_state.data_store["B"]]))
        selected_t = st.selectbox("Select Teacher", teachers)
        personal_data = [x for x in st.session_state.data_store["C"] if x['Teacher'] == selected_t]
        if personal_data:
            st.dataframe(pd.DataFrame(personal_data))
            st.download_button(f"📥 Download {selected_t}'s Report", create_pdf(personal_data, selected_t), f"{selected_t}_Report.pdf")

    # Record display and delete (Original)
    if display_key and nav != "Teacher Personal Report" and st.session_state.data_store[display_key]:
        st.divider()
        st.subheader(f"📋 Record Data: {nav}")
        df_view = pd.DataFrame(st.session_state.data_store[display_key])
        st.dataframe(df_view, use_container_width=True)
        if st.button("🗑️ Remove Last Record"):
            st.session_state.data_store[display_key].pop()
            st.rerun()
