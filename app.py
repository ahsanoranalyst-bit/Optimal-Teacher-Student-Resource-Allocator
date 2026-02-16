

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. INITIALIZATION ---
ACTIVATION_KEY = "PAK-2026"

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "A": [], # Student Performance Records
        "B": [], # Teacher Experts Data
        "School_Name": "Global International Academy"
    }

# Predictive Score Engine
def calculate_predictive_score(a, b, c, d):
    total = a + b + c + d
    if total == 0: return 0
    # Formula: A=100%, B=75%, C=50%, D=25%
    raw_score = ((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total
    return round(raw_score, 2)

# --- 2. PROFESSIONAL PDF ENGINE (Fixed Error) ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.data_store["School_Name"].upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, "OFFICIAL TEACHER DEPLOYMENT & SHUFFLING AUDIT", 0, 1, 'C')
        self.ln(15)

def create_pdf(df, title):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    # Header logic
    col_width = 190 / len(df.columns)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), 1, 0, 'C')
    pdf.ln()
    # Data rows logic
    pdf.set_font('Arial', '', 9)
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, 10, str(val), 1, 0, 'C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MAIN DASHBOARD ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Access Control")
    key_input = st.text_input("Enter Activation Key", type="password")
    if st.button("Authenticate"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    
    # Global Sidebar for Bulk Import
    st.sidebar.header("📂 Bulk Excel Import")
    up_type = st.sidebar.selectbox("Select Category", ["Student Performance", "Teachers"])
    up_file = st.sidebar.file_uploader("Upload XLSX File", type=["xlsx"])
    
    if up_file and st.sidebar.button("Process Bulk Upload"):
        df_up = pd.read_excel(up_file).fillna(0)
        if up_type == "Student Performance":
            for _, r in df_up.iterrows():
                p_score = calculate_predictive_score(int(r['A']), int(r['B']), int(r['C']), int(r['D']))
                st.session_state.data_store["A"].append({
                    "Class": str(r['Class']), "Subject": str(r['Subject']), 
                    "Teacher": str(r.get('Teacher', 'N/A')), "Predictive_Score": p_score
                })
        else:
            for _, r in df_up.iterrows():
                st.session_state.data_store["B"].append({
                    "Name": str(r['Name']), "Expertise": str(r['Expertise']), "Success": int(r['Success'])
                })
        st.sidebar.success(f"{up_type} Imported!")

    nav = st.sidebar.selectbox("Main Menu", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    # --- SECTION A: PERFORMANCE & MANUAL ENTRY ---
    if nav == "Student Performance (A)":
        st.header("📊 Student Performance & Prediction")
        with st.expander("➕ Manual Data Entry"):
            c1, c2, c3 = st.columns(3)
            m_cls = c1.text_input("Class (Grade-1A)")
            m_sub = c2.text_input("Subject")
            m_tchr = c3.text_input("Current Teacher")
            g1, g2, g3, g4 = st.columns(4)
            ma, mb, mc, md = g1.number_input("A count", 0), g2.number_input("B count", 0), g3.number_input("C count", 0), g4.number_input("D count", 0)
            if st.button("Save Record"):
                m_score = calculate_predictive_score(ma, mb, mc, md)
                st.session_state.data_store["A"].append({"Class": m_cls, "Subject": m_sub, "Teacher": m_tchr, "Predictive_Score": m_score})
                st.rerun()

        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_a, use_container_width=True)
            idx_del = st.selectbox("Select Row to Delete", df_a.index)
            if st.button("🗑️ Delete Selected Record"):
                st.session_state.data_store["A"].pop(idx_del)
                st.rerun()

    # --- SECTION B: TEACHER EXPERTS ---
    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Faculty Specialization Registry")
        with st.expander("➕ Manual Teacher Entry"):
            tn = st.text_input("Teacher Name")
            te = st.text_input("Expertise (Subject)")
            ts = st.slider("Success Score", 0, 100, 70)
            if st.button("Register Teacher"):
                st.session_state.data_store["B"].append({"Name": tn, "Expertise": te, "Success": ts})
                st.rerun()

        if st.session_state.data_store["B"]:
            df_b = pd.DataFrame(st.session_state.data_store["B"])
            st.dataframe(df_b, use_container_width=True)
            t_del = st.selectbox("Select Teacher to Remove", df_b.index)
            if st.button("🗑️ Delete Teacher"):
                st.session_state.data_store["B"].pop(t_del)
                st.rerun()

    # --- SECTION C: EFFICIENCY MAPPING & SHUFFLING (The Fix) ---
    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Automated Teacher Shuffling & Audit")
        
        mapping_results = []
        for p in st.session_state.data_store["A"]:
            # Find matching expert for this subject
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == p['Subject']]
            best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0] if matches else None
            
            # Shuffling Logic
            score_val = p['Predictive_Score']
            needs_shuffle = score_val < 50
            
            mapping_results.append({
                "Class": p['Class'],
                "Subject": p['Subject'],
                "Current_Score": f"{score_val}%",
                "Original_Teacher": p['Teacher'],
                "Recommended_Teacher": best_t['Name'] if (needs_shuffle and best_t) else p['Teacher'],
                "Status": "❌ REPLACED" if needs_shuffle else "✅ STABLE",
                "Audit_Action": "SEND TO TRAINING" if needs_shuffle else "RETAIN"
            })

        if mapping_results:
            df_final = pd.DataFrame(mapping_results)
            st.table(df_results := df_final)
            
            st.divider()
            col1, col2 = st.columns(2)
            
            # PDF Generation Fix
            with col1:
                try:
                    pdf_bytes = create_pdf(df_final, "Deployment")
                    st.download_button("📥 Download PDF Audit Report", pdf_bytes, "Teacher_Audit.pdf")
                except:
                    st.error("PDF generation error - check data format.")

            # Excel Generation Fix for Next Project
            with col2:
                xl_buffer = io.BytesIO()
                with pd.ExcelWriter(xl_buffer, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False)
                st.download_button("📊 Export Excel for Scheduling", xl_buffer.getvalue(), "Shuffle_Final_Data.xlsx")
        else:
            st.warning("No data found in Student Performance or Teacher Experts to generate audit.")
