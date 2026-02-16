 

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
    # Predictive Score as the 5th Point logic
    score = ((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total
    return round(score, 2)

# --- 2. PROFESSIONAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        school_name = st.session_state.data_store.get("School_Name", "GLOBAL ACADEMY").upper()
        self.cell(0, 12, school_name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "TEACHER EFFICIENCY & MAPPING REPORT", 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(15)

    def footer(self):
        self.set_y(-30)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "__________________________", 0, 1, 'R')
        self.cell(0, 5, "Academic Director Signature", 0, 1, 'R')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.cell(0, 10, f"Report Date: {timestamp} | Page {self.page_no()}", 0, 0, 'L')

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 10, f"REPORT: {title.upper()}", 0, 1, 'L')
    pdf.ln(5)
    
    if not df.empty:
        # Re-ordered columns to include Predictive Score as key metric
        display_cols = ["Class", "Subject", "Teacher", "Current Score", "Status"]
        col_widths = [25, 40, 45, 35, 45]
        
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(230, 235, 245)
        for i, col in enumerate(display_cols):
            pdf.cell(col_widths[i], 10, col, 1, 0, 'C', fill=True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 9)
        for _, row in df.iterrows():
            for i, col in enumerate(display_cols):
                pdf.cell(col_widths[i], 10, str(row[col]), 1, 0, 'C')
            pdf.ln()
            
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MAIN APP LOGIC ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    key_input = st.text_input("Enter System Key", type="password")
    if st.button("Authenticate"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Invalid Key")

elif not st.session_state.setup_complete:
    st.title("⚙️ Institution Setup")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "Global International Academy")
    if st.button("🚀 Enter Dashboard"):
        st.session_state.setup_complete = True
        st.rerun()

else:
    st.sidebar.title("Navigation")
    nav = st.sidebar.selectbox("Go to", ["Efficiency Mapping (C)", "Data Entry"])

    # --- EFFICIENCY MAPPING (C) ---
    if nav == "Efficiency Mapping (C)":
        st.header("🎯 Efficiency Mapping & Teacher Analysis")
        
        # 1. Manual Entry / Individual Teacher Search
        st.subheader("🔍 Teacher-Wise Performance Search")
        if st.session_state.data_store["B"]:
            teacher_list = [t['Name'] for t in st.session_state.data_store["B"]]
            selected_teacher = st.selectbox("Select Teacher to View Class-wise Report", ["Select..."] + teacher_list)
            
            if selected_teacher != "Select...":
                # Filter data for this specific teacher
                # Note: In a real scenario, this matches mapping in 'C'
                teacher_report_data = [row for row in st.session_state.data_store["C"] if row['Teacher'] == selected_teacher]
                
                if teacher_report_data:
                    tdf = pd.DataFrame(teacher_report_data)
                    st.write(f"### Performance for {selected_teacher}")
                    st.dataframe(tdf, use_container_width=True)
                    
                    pdf_teacher = create_pdf(teacher_report_data, f"Report for {selected_teacher}")
                    st.download_button(f"📥 Download {selected_teacher}'s Report", pdf_teacher, f"{selected_teacher}_Report.pdf")
                else:
                    st.info("No mapping found for this teacher. Please run 'Auto Mapping' or assign manually.")

        st.divider()

        # 2. Bulk Actions
        st.subheader("📦 Bulk Reports & Categories")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Sync & Refresh All Mappings"):
                st.session_state.data_store["C"] = []
                for record in st.session_state.data_store["A"]:
                    matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == record['Subject']]
                    if matches:
                        best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                        status = "BEST PERFORMER" if record['Predictive Score'] >= 60 else "NEEDS IMPROVEMENT"
                        st.session_state.data_store["C"].append({
                            "Class": record['Class'], "Subject": record['Subject'],
                            "Teacher": best_t['Name'], "Current Score": record['Predictive Score'],
                            "Status": status
                        })
                st.success("All records synced!")
                st.rerun()

        # 3. Separate Lists & PDF Downloads
        if st.session_state.data_store["C"]:
            full_df = pd.DataFrame(st.session_state.data_store["C"])
            
            # Separate Data
            best_list = full_df[full_df['Status'] == "BEST PERFORMER"].to_dict('records')
            imp_list = full_df[full_df['Status'] == "NEEDS IMPROVEMENT"].to_dict('records')

            c_best, c_imp = st.columns(2)
            
            with c_best:
                st.markdown("#### ✅ Best Performance Teachers")
                st.write(f"Total: {len(best_list)}")
                if best_list:
                    pdf_best = create_pdf(best_list, "Best Performance List")
                    st.download_button("🟢 Download Best Report (Bulk)", pdf_best, "Best_Teachers.pdf")
            
            with c_imp:
                st.markdown("#### ⚠️ Improvement Needed")
                st.write(f"Total: {len(imp_list)}")
                if imp_list:
                    pdf_imp = create_pdf(imp_list, "Improvement Required List")
                    st.download_button("🔴 Download Improvement Report (Bulk)", pdf_imp, "Improvement_Needed.pdf")

            st.divider()
            st.write("### Full Efficiency Map")
            st.dataframe(full_df, use_container_width=True)

    elif nav == "Data Entry":
        st.info("Please use the sidebar to upload Excel files for Student Performance (A) and Teachers (B).")
