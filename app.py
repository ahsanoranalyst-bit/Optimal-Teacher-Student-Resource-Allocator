https://g.co/gemini/share/b117c03cac08 

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date
import io

# --- 1. CONFIGURATION & LICENSE ---
ACTIVATION_KEY = "PAK-2026"
EXPIRY_DATE = date(2026, 12, 31)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'setup' not in st.session_state: st.session_state.setup = False
if 'school_name' not in st.session_state: st.session_state.school_name = ""
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Classes": [], "Teachers": [], "Efficiency": [], "Feedback": [], "Demands": []
    }

# --- 2. MASTER PDF ENGINE ---
class MasterPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, st.session_state.school_name.upper(), 0, 1, 'C')
        self.set_font('Helvetica', 'I', 10)
        self.cell(0, 10, f"System Generated Report: {self.report_title}", 0, 1, 'C')
        self.ln(10)
        self.line(10, 32, 200, 32)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")} | Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(title, data_list):
    pdf = MasterPDF()
    pdf.report_title = title
    pdf.add_page()
    
    if not data_list:
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, "No records found in this section.", 0, 1)
    else:
        df = pd.DataFrame(data_list)
        # Header
        pdf.set_fill_color(52, 73, 94)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", 'B', 9)
        
        col_width = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        
        # Rows
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", '', 8)
        for _, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, 9, str(item), 1, 0, 'C')
            pdf.ln()
            
    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGICAL ACCESS CONTROL ---
if not st.session_state.auth:
    st.title("🔐 Enterprise System Activation")
    key_input = st.text_input("Enter Activation Key", type="password")
    if st.button("Activate System", use_container_width=True):
        if key_input == ACTIVATION_KEY:
            st.session_state.auth = True
            st.rerun()
        else: st.error("Access Denied: Invalid Key")

elif not st.session_state.setup:
    st.title("🏫 Institution Setup")
    s_name = st.text_input("Enter Registered School Name")
    if st.button("Initialize Dashboard", use_container_width=True):
        if s_name:
            st.session_state.school_name = s_name
            st.session_state.setup = True
            st.rerun()
        else: st.warning("Please provide a valid school name.")

# --- 4. MAIN APPLICATION ---
else:
    st.sidebar.title(f"🏢 {st.session_state.school_name}")
    menu = st.sidebar.selectbox("Navigation Menu", 
        ["Section A: Student Load", "Section B: Teacher Profile", 
         "Section C: Efficiency (Timetable)", "Section D: Feedback", 
         "Teacher Demands", "Smart Analysis Report"])
    
    if st.sidebar.button("Logout / Reset"):
        st.session_state.auth = False
        st.session_state.setup = False
        st.rerun()

    st.title(menu)

    # --- SECTION A: STUDENT LOAD ---
    if menu == "Section A: Student Load":
        with st.form("a_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                g = st.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
                s = st.text_input("Section Name (e.g. A, B, Blue)")
            with col2:
                total_std = st.number_input("Total Students", min_value=1)
                special_std = st.number_input("Students Needing Special Attention", min_value=0)
            needs_desc = st.text_area("Describe Special Needs (Slot for Teacher Attention)")
            
            if st.form_submit_button("Add Class"):
                st.session_state.data_store["Classes"].append({
                    "Grade": g, "Section": s, "Total Students": total_std, 
                    "Special Needs": special_std, "Needs Detail": needs_desc
                })
                st.rerun()
        current_data = st.session_state.data_store["Classes"]

    # --- SECTION B: TEACHER PROFILE ---
    elif menu == "Section B: Teacher Profile":
        with st.form("b_form", clear_on_submit=True):
            t_name = st.text_input("Full Teacher Name")
            t_qual = st.selectbox("Highest Qualification", ["PhD", "Masters", "Bachelors", "Other"])
            t_exp = st.number_input("Years of Experience", min_value=0)
            if st.form_submit_button("Save Teacher Profile"):
                st.session_state.data_store["Teachers"].append({
                    "Name": t_name, "Qualification": t_qual, "Experience": t_exp
                })
                st.rerun()
        current_data = st.session_state.data_store["Teachers"]

    # --- SECTION C: EFFICIENCY ---
    elif menu == "Section C: Efficiency (Timetable)":
        if not st.session_state.data_store["Teachers"]: st.warning("Add Teachers in Section B first.")
        else:
            with st.form("c_form", clear_on_submit=True):
                t_list = [t['Name'] for t in st.session_state.data_store["Teachers"]]
                c_list = [f"{c['Grade']}-{c['Section']}" for c in st.session_state.data_store["Classes"]]
                sel_t = st.selectbox("Select Teacher", t_list)
                sel_c = st.selectbox("Assign to Class/Section", c_list)
                periods = st.number_input("Weekly Periods for this Class", min_value=1)
                admin_h = st.number_input("Weekly Admin/Desk Hours", value=1)
                if st.form_submit_button("Record Efficiency Slot"):
                    st.session_state.data_store["Efficiency"].append({
                        "Teacher": sel_t, "Assigned Class": sel_c, 
                        "Periods": periods, "Admin Hours": admin_h
                    })
                    st.rerun()
        current_data = st.session_state.data_store["Efficiency"]

    # --- SECTION D: FEEDBACK ---
    elif menu == "Section D: Feedback":
        with st.form("d_form", clear_on_submit=True):
            f_source = st.selectbox("Source", ["Student", "Parent", "HOD"])
            f_teacher = st.text_input("Regarding Teacher")
            f_rating = st.slider("Rating (1-10)", 1, 10, 5)
            f_comment = st.text_area("Detailed Feedback")
            if st.form_submit_button("Submit Feedback"):
                st.session_state.data_store["Feedback"].append({
                    "Source": f_source, "Teacher": f_teacher, "Rating": f_rating, "Comments": f_comment
                })
                st.rerun()
        current_data = st.session_state.data_store["Feedback"]

    # --- TEACHER DEMANDS ---
    elif menu == "Teacher Demands":
        with st.form("demand_form", clear_on_submit=True):
            req_by = st.text_input("Requested By (Manager/Admin)")
            req_t = st.text_input("Teacher Requested")
            req_sec = st.text_input("Required for Section")
            if st.form_submit_button("Log Demand"):
                st.session_state.data_store["Demands"].append({
                    "Requester": req_by, "Teacher": req_t, "Section": req_sec, "Date": date.today().strftime("%Y-%m-%d")
                })
                st.rerun()
        current_data = st.session_state.data_store["Demands"]

    # --- SMART ANALYSIS REPORT ---
    else:
        analysis_list = []
        for eff in st.session_state.data_store["Efficiency"]:
            # Logic: (Periods * Weight) + (Admin * Weight) + (Special Needs impact)
            # Find class data to check special needs
            class_info = next((c for c in st.session_state.data_store["Classes"] if f"{c['Grade']}-{c['Section']}" == eff['Assigned Class']), None)
            sp_load = class_info['Special Needs'] * 2 if class_info else 0
            
            # Optimization Score 1-200
            base_score = (eff['Periods'] * 5) + (eff['Admin Hours'] * 8) + sp_load
            final_score = min(200, max(1, int(base_score)))
            
            analysis_list.append({
                "Teacher": eff['Teacher'],
                "Class Assigned": eff['Assigned Class'],
                "Resource Score": final_score,
                "Recommendation": "Optimal" if final_score < 140 else "Reduce Load"
            })
        
        st.subheader("Automated Resource Optimization Index (1-200)")
        if analysis_list:
            st.table(analysis_list)
        current_data = analysis_list

    # --- UNIVERSAL DATA VIEW & PDF EXPORT ---
    if 'current_data' in locals() and current_data:
        st.markdown("---")
        st.write("### Review Records & Export PDF")
        df_view = pd.DataFrame(current_data)
        st.dataframe(df_view, use_container_width=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🗑️ Delete Last Record"):
                key_map = {"Section A": "Classes", "Section B": "Teachers", "Section C": "Efficiency", "Section D": "Feedback", "Teacher Demands": "Demands"}
                key = key_map.get(menu.split(":")[0], menu.replace(" Report", ""))
                if key in st.session_state.data_store and st.session_state.data_store[key]:
                    st.session_state.data_store[key].pop()
                    st.rerun()
        with col_btn2:
            pdf_bytes = generate_pdf(menu, current_data)
            st.download_button(label=f"📥 Download {menu} PDF", data=pdf_bytes, file_name=f"{menu.replace(' ', '_')}.pdf", mime="application/pdf")
