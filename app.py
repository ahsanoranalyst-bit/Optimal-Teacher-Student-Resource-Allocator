import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. CORE INITIALIZATION ---
ACTIVATION_KEY = "Ahsan123"

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

# --- 2. ADVANCED PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        name = st.session_state.data_store.get("School_Name", "ACADEMY").upper()
        self.cell(0, 12, name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "OFFICIAL PERFORMANCE REPORT", 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(20)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, "Authorized Signature: __________________________", 0, 1, 'R')
        ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.cell(0, 10, f"Date: {ts} | Page {self.page_no()}", 0, 0, 'L')

def create_custom_pdf(data, title, header_color=(0,0,0)):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(header_color[0], header_color[1], header_color[2])
    pdf.cell(0, 10, title.upper(), 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    if not df.empty:
        col_widths = {"Class": 20, "Teacher": 35, "Subject": 25, "Efficiency Index": 30, "Status": 35, "Action Plan": 45}
        pdf.set_font('Arial', 'B', 8)
        pdf.set_fill_color(235, 235, 235)
        
        display_cols = [c for c in ["Class", "Teacher", "Subject", "Efficiency Index", "Status", "Action Plan"] if c in df.columns]
        for col in display_cols:
            pdf.cell(col_widths.get(col, 20), 10, col, 1, 0, 'C', fill=True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 7)
        for _, row in df.iterrows():
            for col in display_cols:
                val = f"{row[col]}%" if col == "Efficiency Index" else str(row[col])
                pdf.cell(col_widths.get(col, 20), 8, val, 1, 0, 'C')
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
                    for _, row in df.iterrows():
                        p_score = calculate_predictive_score(int(row['A']), int(row['B']), int(row['C']), int(row['D']))
                        st.session_state.data_store["A"].append({
                            "Class": str(row['Class']), "Subject": str(row['Subject']),
                            "A": int(row['A']), "B": int(row['B']), "C": int(row['C']), "D": int(row['D']),
                            "Student Score": p_score 
                        })
                elif upload_type == "Teachers":
                    for _, row in df.iterrows():
                        st.session_state.data_store["B"].append({
                            "Name": row['Name'], "Expertise": row['Expertise'],
                            "Success": int(row['Success']), "Assigned Class": str(row['Assigned Class'])
                        })
                st.sidebar.success("Import Successful!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

# --- 4. MAIN INTERFACE ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    pwd = st.text_input("Enter Activation Key", type="password")
    if st.button("Login"):
        if pwd == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()

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
    st.sidebar.title("🎮 Dashboard Menu")
    nav = st.sidebar.radio("Go To:", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)", "Analytics Dashboard", "Teacher Portal"])
    handle_bulk_upload()

    if st.sidebar.button("🔓 Logout"):
        st.session_state.authenticated = False
        st.session_state.setup_complete = False
        st.rerun()

    st.title(f"🏫 {st.session_state.data_store['School_Name']}")

    if nav == "Student Performance (A)":
        st.header("📊 Student Performance Records")
        if st.session_state.data_store["A"]:
            st.dataframe(pd.DataFrame(st.session_state.data_store["A"]))

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Teacher Registry")
        if st.session_state.data_store["B"]:
            st.dataframe(pd.DataFrame(st.session_state.data_store["B"]))

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Efficiency Mapping")
        if st.button("🔄 Auto-Map Teachers"):
            st.session_state.data_store["C"] = []
            for teacher in st.session_state.data_store["B"]:
                relevant = [a for a in st.session_state.data_store["A"]
                           if a['Subject'].lower() == teacher['Expertise'].lower()
                           and a['Class'] == teacher['Assigned Class']]
                
                if relevant:
                    for r in relevant:
                        ts = teacher['Success']
                        ps = r['Student Score']
                        combined = (ps * 0.6) + (ts * 0.4)
                        
                        if combined >= 85: status, action = "GOLD STANDARD", "Promote as Mentor"
                        elif ps < 50 and ts < 50: status, action = "CRITICAL: DOUBLE ACTION", "Teacher Training & Remedial Classes"
                        elif combined >= 70: status, action = "BEST TEACHER", "Maintain Performance"
                        else: status, action = "IMPROVEMENT NEEDED", "Closer Monitoring Required"

                        st.session_state.data_store["C"].append({
                            "Class": r['Class'], "Subject": teacher['Expertise'], "Teacher": teacher['Name'],
                            "Teacher Success": ts, "Student Score": ps,
                            "Efficiency Index": round(combined, 2), "Status": status, "Action Plan": action
                        })
            st.success("Mapping Completed!")

        if st.session_state.data_store["C"]:
            df_c = pd.DataFrame(st.session_state.data_store["C"])
            st.dataframe(df_c, use_container_width=True)
            
            # --- RESTORED SEPARATE PDF BUTTONS ---
            best = df_c[df_c["Status"].isin(["BEST TEACHER", "GOLD STANDARD"])]
            improve = df_c[~df_c["Status"].isin(["BEST TEACHER", "GOLD STANDARD"])]
            
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📥 Download Excellence Report (PDF)", 
                                   create_custom_pdf(best, "Teacher Excellence Report", (34, 139, 34)), 
                                   "Excellence_Report.pdf")
            with c2:
                st.download_button("📥 Download Action Plan (PDF)", 
                                   create_custom_pdf(improve, "Teacher Improvement Action Plan", (220, 20, 60)), 
                                   "Action_Plan.pdf")

    elif nav == "Analytics Dashboard":
        st.header("📈 Institutional Optimization Analytics")
        if st.session_state.data_store["C"]:
            df_chart = pd.DataFrame(st.session_state.data_store["C"])
            df_chart['Display_Label'] = df_chart['Teacher'] + " (" + df_chart['Class'] + ")"
            
            green_list = df_chart[df_chart['Efficiency Index'] >= 85]['Display_Label'].unique().tolist()
            orange_list = df_chart[(df_chart['Efficiency Index'] >= 50) & (df_chart['Efficiency Index'] < 85)]['Display_Label'].unique().tolist()
            red_list = df_chart[df_chart['Efficiency Index'] < 50]['Display_Label'].unique().tolist()

            st.subheader("Teacher Efficiency Priority")
            st.bar_chart(df_chart.set_index('Display_Label')['Efficiency Index'])

            st.markdown("### 🛠️ Optimization Guide & Action List")
            st.success(f"🟢 **Green (85+):** {', '.join(green_list) if green_list else 'None'}")
            st.warning(f"🟠 **Orange (50-84):** {', '.join(orange_list) if orange_list else 'None'}")
            st.error(f"🔴 **Red (<50):** {', '.join(red_list) if red_list else 'None'}")
            
            st.divider()
            avg_eff = df_chart['Efficiency Index'].mean()
            st.metric("Institutional Efficiency Avg", f"{round(avg_eff, 2)}%")
            
            st.subheader("📋 Administrative Summary Export")
            st.download_button(
                label="📥 Download Full Analytics Summary (PDF)",
                data=create_custom_pdf(st.session_state.data_store["C"], "Institutional Performance Summary"),
                file_name=f"Full_Academy_Summary_{datetime.now().strftime('%Y%m%d')}.pdf"
            )
        else:
            st.warning("Please run 'Auto-Map Teachers' in Efficiency Mapping first.")

    elif nav == "Teacher Portal":
        st.header("📜 Individual Teacher Portal")
        if st.session_state.data_store["B"]:
            t_names = sorted(list(set([t['Name'] for t in st.session_state.data_store["B"]])))
            sel_t = st.selectbox("Select Teacher", t_names)
            t_data = [x for x in st.session_state.data_store["C"] if x['Teacher'] == sel_t]
            if t_data:
                st.dataframe(pd.DataFrame(t_data), use_container_width=True)
                st.download_button(f"📥 Download {sel_t}'s Performance Report", 
                                   create_custom_pdf(t_data, f"Report: {sel_t}"), 
                                   f"{sel_t}_Report.pdf")
            else:
                st.info("No mapping data found for this teacher.")
