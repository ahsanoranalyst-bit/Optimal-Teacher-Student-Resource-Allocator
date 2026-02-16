
import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. INITIALIZATION & AUTHENTICATION ---
ACTIVATION_KEY = "PAK-2026"

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "A": [], # Student Performance
        "B": [], # Teacher Experts
        "School_Name": "Global International Academy"
    }

# Predictive Score Formula (Point 5)
def calculate_p_score(a, b, c, d):
    total = a + b + c + d
    if total == 0: return 0
    # Weights: A=100, B=75, C=50, D=25
    return round(((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total, 2)

# --- 2. PROFESSIONAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        name = st.session_state.data_store.get("School_Name", "GLOBAL ACADEMY").upper()
        self.cell(0, 10, name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, "TEACHER DEPLOYMENT & PERFORMANCE AUDIT", 0, 1, 'C')
        self.ln(15)

def generate_pdf(df, title):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Report: {title}", 0, 1, 'L')
    pdf.ln(5)
    
    # Table Setup
    pdf.set_font('Arial', 'B', 8)
    col_width = 190 / len(df.columns)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), 1, 0, 'C')
    pdf.ln()
    
    pdf.set_font('Arial', '', 8)
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, 10, str(val), 1, 0, 'C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MAIN DASHBOARD ---
if not st.session_state.authenticated:
    st.title("🔐 Secure System Access")
    if st.text_input("Activation Key", type="password") == ACTIVATION_KEY:
        if st.button("Access Dashboard"): st.session_state.authenticated = True; st.rerun()
else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    
    # Global Sidebar for Excel Import
    st.sidebar.header("📂 Bulk Data Import")
    cat = st.sidebar.selectbox("Category", ["Student Performance", "Teachers"])
    file = st.sidebar.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])
    
    if file and st.sidebar.button("Confirm Upload"):
        df_up = pd.read_excel(file).fillna(0)
        if cat == "Student Performance":
            for _, r in df_up.iterrows():
                # Unified key naming to prevent KeyError
                sc = calculate_p_score(int(r['A']), int(r['B']), int(r['C']), int(r['D']))
                st.session_state.data_store["A"].append({
                    "Class": str(r['Class']), "Subject": str(r['Subject']), 
                    "Teacher": str(r.get('Teacher', 'N/A')), "Final_Score": sc
                })
        else:
            for _, r in df_up.iterrows():
                st.session_state.data_store["B"].append({
                    "Name": str(r['Name']), "Expertise": str(r['Expertise']), "Success": int(r['Success'])
                })
        st.sidebar.success("Import Successful!")

    nav = st.sidebar.selectbox("Navigation", ["Performance (A)", "Faculty (B)", "Mapping (C)"])

    # --- SECTION A ---
    if nav == "Performance (A)":
        st.header("📊 Student Performance & Data Entry")
        with st.expander("➕ Manual Row Entry"):
            c1, c2, c3 = st.columns(3)
            cls, sub, tchr = c1.text_input("Class"), c2.text_input("Subject"), c3.text_input("Teacher")
            g1, g2, g3, g4 = st.columns(4)
            va, vb, vc, vd = g1.number_input("A",0), g2.number_input("B",0), g3.number_input("C",0), g4.number_input("D",0)
            if st.button("Save Data"):
                st.session_state.data_store["A"].append({"Class": cls, "Subject": sub, "Teacher": tchr, "Final_Score": calculate_p_score(va,vb,vc,vd)})
                st.rerun()

        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_a, use_container_width=True)
            if st.button("🗑️ Delete Record"): st.session_state.data_store["A"].pop(); st.rerun()
            
            # Downloads for Section A
            st.download_button("📥 PDF Report", generate_pdf(df_a, "Performance"), "Section_A.pdf")
            xl_a = io.BytesIO()
            df_a.to_excel(xl_a, index=False)
            st.download_button("📊 Excel Export", xl_a.getvalue(), "Section_A.xlsx")

    # --- SECTION B ---
    elif nav == "Faculty (B)":
        st.header("👨‍🏫 Teacher Registry")
        with st.expander("➕ Manual Faculty Add"):
            fn, fe, fs = st.text_input("Full Name"), st.text_input("Specialization"), st.slider("Success %", 0, 100, 70)
            if st.button("Add Faculty"):
                st.session_state.data_store["B"].append({"Name": fn, "Expertise": fe, "Success": fs})
                st.rerun()
        
        if st.session_state.data_store["B"]:
            df_b = pd.DataFrame(st.session_state.data_store["B"])
            st.dataframe(df_b, use_container_width=True)
            if st.button("🗑️ Remove Last"): st.session_state.data_store["B"].pop(); st.rerun()
            
            # Downloads for Section B
            st.download_button("📥 PDF Faculty List", generate_pdf(df_b, "Faculty"), "Section_B.pdf")

    # --- SECTION C: SHUFFLING & AUDIT (FIXED SECTION) ---
    elif nav == "Mapping (C)":
        st.header("🎯 Deployment Audit & Shuffling Results")
        
        final_audit = []
        # Error Fix: Ensuring consistent key 'Final_Score'
        for entry in st.session_state.data_store["A"]:
            subj = entry['Subject']
            score = entry['Final_Score']
            
            # Find best expert for the subject
            experts = [t for t in st.session_state.data_store["B"] if t['Expertise'] == subj]
            top_teacher = sorted(experts, key=lambda x: x['Success'], reverse=True)[0] if experts else None
            
            # Shuffling Logic: Replaced if score < 50%
            is_shuffled = score < 50
            
            final_audit.append({
                "Class": entry['Class'],
                "Subject": subj,
                "Result": f"{score}%",
                "Old_Teacher": entry['Teacher'],
                "Assigned_Teacher": top_teacher['Name'] if (is_shuffled and top_teacher) else entry['Teacher'],
                "Audit_Status": "❌ REPLACED" if is_shuffled else "✅ STABLE",
                "Quality": "BEST EXPERT" if not is_shuffled else "NEEDS TRAINING"
            })

        if final_audit:
            df_c = pd.DataFrame(final_audit)
            st.table(df_c)
            
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                pdf_c = generate_pdf(df_c, "Final Shuffling Audit")
                st.download_button("📥 Download Final PDF Audit", pdf_c, "Final_Audit_Report.pdf")
            
            with col2:
                xl_c = io.BytesIO()
                df_c.to_excel(xl_c, index=False)
                st.download_button("📊 Export Scheduling Sheet (Excel)", xl_c.getvalue(), "Shuffle_Final.xlsx")
        else:
            st.warning("Please input data in Section A and B first.")
