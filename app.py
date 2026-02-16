

import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# --- 1. CORE LOGIC & SETTINGS ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {"A": [], "B": [], "School_Name": "Global International Academy"}

def calculate_auto_score(row):
    """Automatically calculates score from grades A, B, C, D"""
    try:
        a, b, c, d = int(row['A']), int(row['B']), int(row['C']), int(row['D'])
        total = a + b + c + d
        if total == 0: return 0
        # Weighted Formula: A=100%, B=75%, C=50%, D=25%
        return round(((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total, 2)
    except:
        return 0

# --- 2. UNIVERSAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.data_store["School_Name"].upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, "AUTOMATED ACADEMIC AUDIT & SHUFFLING SYSTEM", 0, 1, 'C')
        self.ln(15)

def get_pdf_report(df, title):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, f"Report Type: {title}", 0, 1, 'L')
    pdf.ln(5)
    
    col_width = 190 / len(df.columns)
    pdf.set_font('Arial', 'B', 7)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), 1, 0, 'C')
    pdf.ln()
    
    pdf.set_font('Arial', '', 7)
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, 10, str(val), 1, 0, 'C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. DASHBOARD INTERFACE ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Login")
    if st.text_input("System Access Key", type="password") == "PAK-2026":
        if st.button("Unlock System"):
            st.session_state.authenticated = True
            st.rerun()
else:
    st.sidebar.title("⚙️ Control Panel")
    
    # Auto-Processing Import
    st.sidebar.header("📥 Upload Student Sheet")
    file = st.sidebar.file_uploader("Drop your Excel file here", type=["xlsx"])
    
    if file and st.sidebar.button("Run Auto-Analysis"):
        df_raw = pd.read_excel(file).fillna(0)
        st.session_state.data_store["A"] = [] # Reset for new analysis
        
        for _, row in df_raw.iterrows():
            # Logic: Auto-calculate Score and assign Profit Level (1-200)
            p_score = calculate_auto_score(row)
            st.session_state.data_store["A"].append({
                "Class": row['Class'],
                "Subject": row['Subject'],
                "Current_Teacher": row.get('Teacher', 'N/A'),
                "Predictive_Score": p_score,
                "Profit_Level": 150 # Auto-assigned fixed profit level
            })
        st.sidebar.success("Analysis Complete!")

    # Navigation Menu
    menu = st.sidebar.selectbox("Go To", ["Live Performance (A)", "Deployment Audit (C)"])

    if menu == "Live Performance (A)":
        st.header("📊 Student Performance Analysis")
        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_a, use_container_width=True)
            st.download_button("📥 Download PDF Report", get_pdf_report(df_a, "Performance"), "Section_A.pdf")

    elif menu == "Deployment Audit (C)":
        st.header("🎯 Automated Teacher Shuffling")
        # For this logic to work, you'd need Teacher data in session_state.data_store["B"]
        # Assuming some default experts are available for logic demonstration
        
        final_results = []
        for p in st.session_state.data_store["A"]:
            # Logic: If Score < 50, system suggests "REPLACEMENT"
            is_low = p['Predictive_Score'] < 50
            
            final_results.append({
                "Class": p['Class'],
                "Subject": p['Subject'],
                "Performance": f"{p['Predictive_Score']}%",
                "Original_Staff": p['Current_Teacher'],
                "Status": "❌ NEEDS SHUFFLING" if is_low else "✅ STABLE",
                "Profit": p['Profit_Level'],
                "Action": "TRANSFER TO TRAINING" if is_low else "RETAIN AS BEST"
            })
        
        if final_results:
            df_c = pd.DataFrame(final_results)
            st.table(df_c)
            
            # Export Buttons
            st.download_button("📥 Download Final Audit (PDF)", get_pdf_report(df_c, "Deployment Audit"), "Final_Audit.pdf")
            xl_io = io.BytesIO()
            df_c.to_excel(xl_io, index=False)
            st.download_button("📊 Export for Next Project (Excel)", xl_io.getvalue(), "Shuffle_Data.xlsx")
