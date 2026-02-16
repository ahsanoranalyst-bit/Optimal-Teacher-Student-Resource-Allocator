import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# --- 1. CORE LOGIC ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {"A": [], "B": [], "School_Name": "Global International Academy"}

def calculate_auto_score(a, b, c, d):
    """Calculates Predictive Score as the 5th point [cite: 2026-02-14]"""
    total = a + b + c + d
    if total == 0: return 0
    return round(((a * 100) + (b * 75) + (c * 50) + (d * 25)) / total, 2)

# --- 2. PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.data_store["School_Name"].upper(), 0, 1, 'C')
        self.ln(15)

def get_pdf_report(df, title):
    pdf = SchoolPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, title, 0, 1, 'L')
    pdf.ln(5)
    col_width = 190 / len(df.columns)
    pdf.set_font('Arial', 'B', 8)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), 1, 0, 'C')
    pdf.ln()
    pdf.set_font('Arial', '', 8)
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, 10, str(val), 1, 0, 'C')
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. DASHBOARD ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Login")
    if st.text_input("Key", type="password") == "PAK-2026":
        if st.button("Unlock"): st.session_state.authenticated = True; st.rerun()
else:
    st.sidebar.title("Settings")
    
    # Uploading Option [cite: 2026-02-10]
    st.sidebar.header("📂 Bulk Upload")
    file = st.sidebar.file_uploader("Upload Student Excel", type=["xlsx"])
    if file and st.sidebar.button("Import Data"):
        df_raw = pd.read_excel(file).fillna(0)
        for _, r in df_raw.iterrows():
            score = calculate_auto_score(r['A'], r['B'], r['C'], r['D'])
            st.session_state.data_store["A"].append({
                "Class": r['Class'], "Subject": r['Subject'], 
                "Teacher": r.get('Teacher', 'TBD'), "Score": score
            })
        st.sidebar.success("Imported!")

    menu = st.sidebar.selectbox("Navigation", ["Student Performance (A)", "Teacher Experts (B)", "Mapping & Shuffling (C)"])

    # SECTION A: Performance & Manual Entry
    if menu == "Student Performance (A)":
        st.header("📊 Section A: Performance")
        with st.expander("➕ Manual Entry"):
            c1, c2, c3 = st.columns(3)
            m_cls, m_sub, m_tch = c1.text_input("Class"), c2.text_input("Subject"), c3.text_input("Teacher")
            g1, g2, g3, g4 = st.columns(4)
            ma, mb, mc, md = g1.number_input("A", 0), g2.number_input("B", 0), g3.number_input("C", 0), g4.number_input("D", 0)
            if st.button("Save Entry"):
                score = calculate_auto_score(ma, mb, mc, md)
                st.session_state.data_store["A"].append({"Class": m_cls, "Subject": m_sub, "Teacher": m_tch, "Score": score})
                st.rerun()
        
        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_a)
            st.download_button("📥 PDF Section A", get_pdf_report(df_a, "Performance"), "Section_A.pdf")

    # SECTION B: Teacher Experts (Restored) [cite: 2026-02-10]
    elif menu == "Teacher Experts (B)":
        st.header("👨‍🏫 Section B: Registry")
        with st.expander("➕ Register Teacher"):
            tn, te, ts = st.text_input("Name"), st.text_input("Expertise"), st.slider("Success Rate", 0, 100, 75)
            if st.button("Add"):
                st.session_state.data_store["B"].append({"Name": tn, "Expertise": te, "Success": ts})
                st.rerun()
        if st.session_state.data_store["B"]:
            df_b = pd.DataFrame(st.session_state.data_store["B"])
            st.dataframe(df_b)
            st.download_button("📥 PDF Section B", get_pdf_report(df_b, "Teachers"), "Section_B.pdf")

    # SECTION C: Mapping & Profit Level [cite: 2025-12-29, 2026-02-12]
    elif menu == "Mapping & Shuffling (C)":
        st.header("🎯 Section C: Audit")
        results = []
        for p in st.session_state.data_store["A"]:
            experts = [t for t in st.session_state.data_store["B"] if t['Expertise'] == p['Subject']]
            best = sorted(experts, key=lambda x: x['Success'], reverse=True)[0] if experts else None
            is_low = p['Score'] < 50
            results.append({
                "Class": p['Class'], "Old_Teacher": p['Teacher'], "Score": f"{p['Score']}%",
                "New_Teacher": best['Name'] if (is_low and best) else p['Teacher'],
                "Profit_Level": 150, "Status": "❌ SHUFFLED" if is_low else "✅ STABLE"
            })
        if results:
            df_c = pd.DataFrame(results)
            st.table(df_c)
            st.download_button("📥 PDF Final Audit", get_pdf_report(df_c, "Final Audit"), "Final_Audit.pdf")
