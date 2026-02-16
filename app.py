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
    
    if "Institution" in df.columns:
        df["Institution"] = st.session_state.data_store.get("School_Name", "Global International Academy")

    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 10, f"DOCUMENT SECTION: {title.upper()}", 0, 1, 'L')
    pdf.set_draw_color(31, 73, 125)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    if not df.empty:
        column_widths = {
            "Institution": 50, "Class": 20, "Subject": 25,
            "Teacher": 35, "Current Score": 30, "Status": 30
        }
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
                val = str(row[col]) if pd.notnull(row[col]) else ""
                w = column_widths.get(col, default_w)
                pdf.cell(w, 9, val, 1, 0, 'C', fill=True)
            pdf.ln()
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
        if st.button("🚀 Enter Dashboard"):
            st.session_state.setup_complete = True
            st.rerun()

else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    if nav == "Student Performance (A)":
        st.header("📊 Performance Records & Prediction")
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        if class_list:
            with st.expander("➕ Manual Entry"):
                sel_class = st.selectbox("Class", class_list)
                sel_sub = st.selectbox("Subject", st.session_state.data_store["Grades_Config"][sel_class])
                with st.form("a_form"):
                    c1,c2,c3,c4 = st.columns(4)
                    ga,gb,gc,gd = c1.number_input("A",0), c2.number_input("B",0), c3.number_input("C",0), c4.number_input("D",0)
                    if st.form_submit_button("Save & Calculate Score"):
                        p_score = calculate_predictive_score(ga, gb, gc, gd)
                        st.session_state.data_store["A"].append({
                            "Class": sel_class, "Subject": sel_sub,
                            "A": ga, "B": gb, "C": gc, "D": gd,
                            "Total": ga+gb+gc+gd,
                            "Predictive Score": p_score
                        })
                        st.rerun()
        
        if st.session_state.data_store["A"]:
            df_view = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_view, use_container_width=True)
            pdf_bytes = create_pdf(st.session_state.data_store["A"], "Student Performance Report")
            st.download_button("📥 Download Performance PDF", pdf_bytes, "Performance_Report.pdf")

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Faculty Specialization")
        all_subs = set()
        for s_list in st.session_state.data_store["Grades_Config"].values(): all_subs.update(s_list)
        with st.form("b_form"):
            t_name = st.text_input("Teacher Name")
            t_exp = st.selectbox("Expertise", list(all_subs) if all_subs else ["N/A"])
            t_rate = st.slider("Historical Success %", 0, 100, 80)
            if st.form_submit_button("Register"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_rate})
                st.rerun()
        
        if st.session_state.data_store["B"]:
            df_view = pd.DataFrame(st.session_state.data_store["B"])
            st.dataframe(df_view, use_container_width=True)
            pdf_bytes = create_pdf(st.session_state.data_store["B"], "Teacher Expertise Report")
            st.download_button("📥 Download Teacher PDF", pdf_bytes, "Teacher_Report.pdf")

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Strategic Deployment & PDF Generation")
        
        if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
            # --- FORM FOR ALLOCATION ---
            with st.expander("🆕 Add New Mapping/Allocation"):
                options = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
                sel = st.selectbox("Select Class & Subject", options)
                parts = sel.split(" | ")
                
                class_data = next((x for x in st.session_state.data_store["A"] if x['Class'] == parts[0] and x['Subject'] == parts[1]), None)
                matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == parts[1]]
                
                if matches and class_data:
                    best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                    st.write(f"Recommended Teacher: **{best_t['Name']}** (Rating: {best_t['Success']}%)")
                    st.write(f"Current Class Predictive Score: **{class_data['Predictive Score']}%**")
                    
                    if st.button("Authorize Allocation"):
                        status = "BEST PERFORMER" if class_data['Predictive Score'] >= 60 else "NEEDS IMPROVEMENT"
                        st.session_state.data_store["C"].append({
                            "Institution": st.session_state.data_store["School_Name"],
                            "Class": parts[0], "Subject": parts[1],
                            "Teacher": best_t['Name'],
                            "Current Score": class_data['Predictive Score'],
                            "Status": status
                        })
                        st.success("Allocation Recorded.")
                        st.rerun()

            # --- DUAL PDF GENERATION LOGIC ---
            if st.session_state.data_store["C"]:
                mapping_df = pd.DataFrame(st.session_state.data_store["C"])
                
                # Filter Lists
                improvement_data = mapping_df[mapping_df['Status'] == "NEEDS IMPROVEMENT"].to_dict('records')
                best_teacher_data = mapping_df[mapping_df['Status'] == "BEST PERFORMER"].to_dict('records')
                
                st.divider()
                st.subheader("📊 Deployment Statistics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.error(f"🔴 Improvement Needed: {len(improvement_data)}")
                    if improvement_data:
                        pdf_imp = create_pdf(improvement_data, "Teacher Improvement List")
                        st.download_button("📥 Download Improvement PDF", pdf_imp, "Improvement_List.pdf")
                    else:
                        st.write("No teachers in improvement list.")

                with col2:
                    st.success(f"🟢 Best Performers: {len(best_teacher_data)}")
                    if best_teacher_data:
                        pdf_best = create_pdf(best_teacher_data, "Best Teacher Performance List")
                        st.download_button("📥 Download Best Teachers PDF", pdf_best, "Best_Performers_List.pdf")
                    else:
                        st.write("No teachers in best performers list.")

                st.divider()
                st.write("### 📋 All Active Mappings")
                st.dataframe(mapping_df, use_container_width=True)
                
                if st.button("🗑️ Clear All Mappings"):
                    st.session_state.data_store["C"] = []
                    st.rerun()
