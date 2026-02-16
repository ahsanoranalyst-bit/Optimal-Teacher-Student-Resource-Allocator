import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. CORE INITIALIZATION ---
ACTIVATION_KEY = "PAK-2026"

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "A": [], # Student Performance
        "B": [], # Teacher Experts
        "School_Name": "Global International Academy"
    }

def calculate_predictive_score(a, b, c, d):
    total = a + b + c + d
    return round(((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total, 2) if total > 0 else 0

# --- 2. UNIVERSAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.data_store["School_Name"].upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, "OFFICIAL SYSTEM GENERATED REPORT", 0, 1, 'C')
        self.ln(15)

def create_pdf(df, title):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, f"Section: {title}", 0, 1, 'L')
    pdf.ln(5)
    
    # Table Header
    pdf.set_font('Arial', 'B', 8)
    col_width = 190 / len(df.columns)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), 1, 0, 'C')
    pdf.ln()
    
    # Table Data
    pdf.set_font('Arial', '', 8)
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, 10, str(val), 1, 0, 'C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MAIN APP INTERFACE ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access")
    if st.text_input("Enter Key", type="password") == ACTIVATION_KEY:
        if st.button("Login"): st.session_state.authenticated = True; st.rerun()
else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    
    # Global Sidebar for Bulk Import
    st.sidebar.header("📂 Bulk Import (Excel)")
    up_type = st.sidebar.selectbox("Choose Category", ["Student Performance", "Teachers"])
    up_file = st.sidebar.file_uploader("Upload XLSX File", type=["xlsx"])
    if up_file and st.sidebar.button("Confirm Import"):
        df_up = pd.read_excel(up_file).fillna(0)
        if up_type == "Student Performance":
            for _, r in df_up.iterrows():
                score = calculate_predictive_score(int(r['A']), int(r['B']), int(r['C']), int(r['D']))
                st.session_state.data_store["A"].append({"Class": str(r['Class']), "Subject": str(r['Subject']), "Current_Teacher": str(r.get('Teacher', 'N/A')), "Predictive_Score": score})
        else:
            for _, r in df_up.iterrows():
                st.session_state.data_store["B"].append({"Name": str(r['Name']), "Expertise": str(r['Expertise']), "Success": int(r['Success'])})
        st.sidebar.success("Import Successful!")

    nav = st.sidebar.selectbox("Navigate System", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    # --- SECTION A ---
    if nav == "Student Performance (A)":
        st.header("📊 Performance Data & Prediction")
        with st.expander("➕ Add Manual Entry"):
            c1, c2, c3 = st.columns(3)
            m_cls, m_sub, m_t = c1.text_input("Class"), c2.text_input("Subject"), c3.text_input("Current Teacher")
            g1, g2, g3, g4 = st.columns(4)
            ma, mb, mc, md = g1.number_input("A",0), g2.number_input("B",0), g3.number_input("C",0), g4.number_input("D",0)
            if st.button("Save Record"):
                st.session_state.data_store["A"].append({"Class": m_cls, "Subject": m_sub, "Current_Teacher": m_t, "Predictive_Score": calculate_predictive_score(ma,mb,mc,md)})
                st.rerun()

        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_a, use_container_width=True)
            if st.button("🗑️ Delete Last Row"): st.session_state.data_store["A"].pop(); st.rerun()
            
            # Downloads for Section A
            st.download_button("📥 Download Section A (PDF)", create_pdf(df_a, "Student Performance"), "Student_Report.pdf")
            xl_a = io.BytesIO()
            df_a.to_excel(xl_a, index=False)
            st.download_button("📊 Export Section A (Excel)", xl_a.getvalue(), "Student_Data.xlsx")

    # --- SECTION B ---
    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Teacher Registry")
        with st.expander("➕ Add Manual Teacher"):
            tn, te, ts = st.text_input("Name"), st.text_input("Expertise"), st.slider("Success Rate", 0, 100, 70)
            if st.button("Add Teacher"):
                st.session_state.data_store["B"].append({"Name": tn, "Expertise": te, "Success": ts})
                st.rerun()
        
        if st.session_state.data_store["B"]:
            df_b = pd.DataFrame(st.session_state.data_store["B"])
            st.dataframe(df_b, use_container_width=True)
            if st.button("🗑️ Delete Last Row"): st.session_state.data_store["B"].pop(); st.rerun()
            
            # Downloads for Section B
            st.download_button("📥 Download Section B (PDF)", create_pdf(df_b, "Teacher Registry"), "Teacher_Report.pdf")
            xl_b = io.BytesIO()
            df_b.to_excel(xl_b, index=False)
            st.download_button("📊 Export Section B (Excel)", xl_b.getvalue(), "Teacher_Data.xlsx")

    # --- SECTION C (THE AUDIT) ---
    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Shuffling Audit & Next Project Data")
        
        audit_data = []
        for p in st.session_state.data_store["A"]:
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == p['Subject']]
            # Best Expert Selection Logic
            best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0] if matches else None
            
            needs_shuffle = p['Predictive_Score'] < 50
            
            audit_data.append({
                "Class": p['Class'],
                "Subject": p['Subject'],
                "Original_Teacher": p['Current_Teacher'],
                "Result_Score": f"{p['Predictive_Score']}%",
                "New_Teacher": best_t['Name'] if (needs_shuffle and best_t) else p['Current_Teacher'],
                "Action": "❌ SHUFFLED (Training Needed)" if needs_shuffle else "✅ RETAINED (Best Performance)",
                "Quality_Status": "BEST" if not needs_shuffle else "IMPROVEMENT REQ"
            })

        if audit_data:
            df_c = pd.DataFrame(audit_data)
            st.table(df_c)
            
            # PDF & EXCEL for C (Critical for Next Project)
            pdf_c = create_pdf(df_c, "Deployment Audit")
            st.download_button("📥 Download Final Audit (PDF)", pdf_c, "Final_Audit.pdf")
            
            xl_c = io.BytesIO()
            df_c.to_excel(xl_c, index=False)
            st.download_button("📊 Export Scheduling Sheet (Excel)", xl_c.getvalue(), "Scheduling_Data.xlsx")
        else:
            st.info("No data available for mapping. Please input Performance and Teacher data.")
