

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
        "A": [], # Student Performance Records
        "B": [], # Teacher Experts Data
        "School_Name": "Global International Academy"
    }

# Predictive Score Formula Logic
def calculate_p_score(a, b, c, d):
    total = a + b + c + d
    if total == 0: return 0
    return round(((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total, 2)

# --- 2. UNIVERSAL PDF GENERATOR ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        name = st.session_state.data_store.get("School_Name", "GLOBAL ACADEMY").upper()
        self.cell(0, 10, name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, "OFFICIAL ACADEMIC AUDIT & SHUFFLING REPORT", 0, 1, 'C')
        self.ln(15)

def get_pdf_download(df, title):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, f"Section Report: {title}", 0, 1, 'L')
    pdf.ln(5)
    
    # Table Header
    pdf.set_font('Arial', 'B', 8)
    col_width = 190 / len(df.columns)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), 1, 0, 'C')
    pdf.ln()
    
    # Table Body
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
        if st.button("Unlock Dashboard"): st.session_state.authenticated = True; st.rerun()
else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    
    # Sidebar: Bulk Import (A & B)
    st.sidebar.header("📂 Data Import (Excel)")
    cat = st.sidebar.selectbox("Choose Category", ["Student Performance", "Teachers"])
    file = st.sidebar.file_uploader("Upload XLSX File", type=["xlsx"])
    if file and st.sidebar.button("Process Import"):
        df_up = pd.read_excel(file).fillna(0)
        if cat == "Student Performance":
            for _, r in df_up.iterrows():
                # Fix: Standardized Key Name
                sc = calculate_p_score(int(r['A']), int(r['B']), int(r['C']), int(r['D']))
                st.session_state.data_store["A"].append({
                    "Class": str(r['Class']), "Subject": str(r['Subject']), 
                    "Teacher": str(r.get('Teacher', 'Unknown')), "Score": sc
                })
        else:
            for _, r in df_up.iterrows():
                st.session_state.data_store["B"].append({
                    "Name": str(r['Name']), "Expertise": str(r['Expertise']), "Success": int(r['Success'])
                })
        st.sidebar.success("Data Uploaded Successfully!")

    nav = st.sidebar.selectbox("Navigate Menu", ["Performance (A)", "Faculty (B)", "Mapping & Shuffling (C)"])

    # --- SECTION A: PERFORMANCE ---
    if nav == "Performance (A)":
        st.header("📊 Student Results & Manual Entry")
        with st.expander("➕ Manual Row Entry"):
            c1, c2, c3 = st.columns(3)
            cls, sub, tchr = c1.text_input("Class ID"), c2.text_input("Subject Name"), c3.text_input("Teacher Name")
            g1, g2, g3, g4 = st.columns(4)
            va, vb, vc, vd = g1.number_input("A",0), g2.number_input("B",0), g3.number_input("C",0), g4.number_input("D",0)
            if st.button("Save Record"):
                st.session_state.data_store["A"].append({"Class": cls, "Subject": sub, "Teacher": tchr, "Score": calculate_p_score(va,vb,vc,vd)})
                st.rerun()

        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_a, use_container_width=True)
            if st.button("🗑️ Delete Last Entry"): st.session_state.data_store["A"].pop(); st.rerun()
            
            # Downloads for Section A
            st.download_button("📥 Download A (PDF)", get_pdf_download(df_a, "Performance"), "Section_A.pdf")
            xl_a = io.BytesIO()
            df_a.to_excel(xl_a, index=False)
            st.download_button("📊 Export A (Excel)", xl_a.getvalue(), "Section_A.xlsx")

    # --- SECTION B: FACULTY ---
    elif nav == "Faculty (B)":
        st.header("👨‍🏫 Teacher Specialization Registry")
        with st.expander("➕ Manual Faculty Add"):
            fn, fe, fs = st.text_input("Name"), st.text_input("Expertise (Subject)"), st.slider("Success %", 0, 100, 75)
            if st.button("Add Faculty"):
                st.session_state.data_store["B"].append({"Name": fn, "Expertise": fe, "Success": fs})
                st.rerun()
        
        if st.session_state.data_store["B"]:
            df_b = pd.DataFrame(st.session_state.data_store["B"])
            st.dataframe(df_b, use_container_width=True)
            if st.button("🗑️ Remove Last Faculty"): st.session_state.data_store["B"].pop(); st.rerun()
            
            # Downloads for Section B
            st.download_button("📥 Download B (PDF)", get_pdf_download(df_b, "Faculty"), "Section_B.pdf")
            xl_b = io.BytesIO()
            df_b.to_excel(xl_b, index=False)
            st.download_button("📊 Export B (Excel)", xl_b.getvalue(), "Section_B.xlsx")

    # --- SECTION C: MAPPING & SHUFFLING (FIXED ERROR SECTION) ---
    elif nav == "Mapping & Shuffling (C)":
        st.header("🎯 Automatic Teacher Shuffling & Deployment Audit")
        
        audit_results = []
        # Error Prevention: Standardized Dictionary Access
        for item in st.session_state.data_store["A"]:
            current_subject = item['Subject']
            current_score = item['Score'] # Standardized key used here
            
            # Match best available teacher for this subject
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == current_subject]
            best_expert = sorted(matches, key=lambda x: x['Success'], reverse=True)[0] if matches else None
            
            # Logic: If performance < 50%, shuffle with the best available expert
            needs_shuffling = current_score < 50
            
            audit_results.append({
                "Class": item['Class'],
                "Subject": current_subject,
                "Old_Teacher": item['Teacher'],
                "Score_Earned": f"{current_score}%",
                "New_Assigned": best_expert['Name'] if (needs_shuffling and best_expert) else item['Teacher'],
                "Status": "❌ REPLACED" if needs_shuffling else "✅ RETAINED",
                "Action": "TRANSFER TO TRAINING" if needs_shuffling else "KEEP AS BEST"
            })

        if audit_results:
            df_c = pd.DataFrame(audit_results)
            st.table(df_c)
            
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                # PDF Generation for Final Shuffling
                pdf_c = get_pdf_download(df_c, "Final Shuffling Audit")
                st.download_button("📥 Download Final Audit (PDF)", pdf_c, "Final_Audit_Report.pdf")
            
            with col2:
                # Excel Generation for Next Project Use
                xl_c = io.BytesIO()
                df_c.to_excel(xl_c, index=False)
                st.download_button("📊 Export Scheduling Data (Excel)", xl_c.getvalue(), "Shuffle_Final.xlsx")
        else:
            st.warning("Please ensure Student Performance (A) and Teacher Data (B) are entered correctly.")
