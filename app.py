

import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# --- 1. SETTINGS & AUTHENTICATION ---
# Profit level logic
PROFIT_MIN = 1
PROFIT_MAX = 200

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {"A": [], "B": [], "School_Name": "Global International Academy"}

def calculate_p_score(a, b, c, d):
    """Calculates the 5th point: Predictive Score"""
    total = a + b + c + d
    if total == 0: return 0
    return round(((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total, 2)

# --- 2. PDF GENERATION ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.data_store["School_Name"].upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, "OFFICIAL ACADEMIC PERFORMANCE & AUDIT REPORT", 0, 1, 'C')
        self.ln(15)

def get_pdf_bytes(df, title):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Section: {title}", 0, 1, 'L')
    pdf.ln(5)
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

# --- 3. MAIN APPLICATION ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Login")
    if st.text_input("Activation Key", type="password") == "PAK-2026":
        if st.button("Unlock"):
            st.session_state.authenticated = True
            st.rerun()
else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    
    # Sidebar: Bulk Import
    st.sidebar.header("📂 Bulk Import")
    cat = st.sidebar.selectbox("Category", ["Student Performance", "Teachers"])
    file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])
    if file and st.sidebar.button("Process File"):
        df_up = pd.read_excel(file).fillna(0)
        if cat == "Student Performance":
            for _, r in df_up.iterrows():
                score = calculate_p_score(int(r['A']), int(r['B']), int(r['C']), int(r['D']))
                st.session_state.data_store["A"].append({
                    "Class": str(r['Class']), "Subject": str(r['Subject']), 
                    "Teacher": str(r.get('Teacher', 'TBD')), "Score": score
                })
        else:
            for _, r in df_up.iterrows():
                st.session_state.data_store["B"].append({
                    "Name": str(r['Name']), "Expertise": str(r['Expertise']), "Success": int(r['Success'])
                })
        st.sidebar.success("Imported Successfully!")

    menu = st.sidebar.selectbox("Menu", ["Performance (A)", "Teachers (B)", "Mapping & Shuffling (C)"])

    # Section A
    if menu == "Performance (A)":
        st.header("📊 Student Performance Data")
        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_a, use_container_width=True)
            st.download_button("📥 Download PDF", get_pdf_bytes(df_a, "Performance"), "Section_A.pdf")
            if st.button("🗑️ Delete Last Row"):
                st.session_state.data_store["A"].pop()
                st.rerun()

    # Section B
    elif menu == "Teachers (B)":
        st.header("👨‍🏫 Teacher Registry")
        if st.session_state.data_store["B"]:
            df_b = pd.DataFrame(st.session_state.data_store["B"])
            st.dataframe(df_b, use_container_width=True)
            st.download_button("📥 Download PDF", get_pdf_bytes(df_b, "Teachers"), "Section_B.pdf")

    # Section C: Shuffling Logic
    elif menu == "Mapping & Shuffling (C)":
        st.header("🎯 Shuffling & Deployment Audit")
        audit = []
        for p in st.session_state.data_store["A"]:
            # Logic: Driver picks farthest first, drops nearest first
            experts = [t for t in st.session_state.data_store["B"] if t['Expertise'] == p['Subject']]
            best = sorted(experts, key=lambda x: x['Success'], reverse=True)[0] if experts else None
            
            needs_shuffle = p['Score'] < 50
            audit.append({
                "Class": p['Class'], "Subject": p['Subject'], "Old_Teacher": p['Teacher'],
                "Score": f"{p['Score']}%",
                "New_Teacher": best['Name'] if (needs_shuffle and best) else p['Teacher'],
                "Status": "❌ SHUFFLED" if needs_shuffle else "✅ RETAINED",
                "Remark": "SEND TO TRAINING" if needs_shuffle else "BEST"
            })
        
        if audit:
            df_c = pd.DataFrame(audit)
            st.table(df_c)
            st.download_button("📥 Download Audit PDF", get_pdf_bytes(df_c, "Audit"), "Final_Audit.pdf")
            xl_c = io.BytesIO()
            df_c.to_excel(xl_c, index=False)
            st.download_button("📊 Export for Scheduling (Excel)", xl_c.getvalue(), "Shuffle_Final.xlsx")
