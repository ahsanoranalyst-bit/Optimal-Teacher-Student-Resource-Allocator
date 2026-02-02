

import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# --- PDF Generation Logic (Internal Function) ---
def export_pdf(df_a, df_c, inst_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 15, txt=inst_name, ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Executive Performance Summary", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Student Academic Breakdown:", ln=True)
    pdf.set_font("Arial", '', 10)
    for _, row in df_a.iterrows():
        pdf.cell(200, 8, txt=f"Class: {row['Class']} | Subject: {row['Subject']} | Grades: A:{row['A']} B:{row['B']} C:{row['C']} D:{row['D']}", ln=True)
    
    if not df_c.empty:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Teacher Deployment Impact (Profit Level 1-200):", ln=True)
        pdf.set_font("Arial", '', 10)
        for _, row in df_c.iterrows():
            pdf.cell(200, 8, txt=f"Teacher: {row['Teacher']} | Impact: {row['Impact']} | Class: {row['Class']}", ln=True)
            
    return pdf.output(dest='S').encode('latin-1')

# --- Main App Logic ---
if "data_store" not in st.session_state:
    st.session_state.data_store = {"A": [], "B": [], "C": []}

nav = st.sidebar.radio("Navigation", ["Student Performance (A)", "Teacher Profiles (B)", "Efficiency Mapping (C)", "Institution Summary"])

if nav == "Student Performance (A)":
    st.header("📊 Student Performance Entry")
    with st.form("a_form"):
        s_class = st.text_input("Class Name")
        s_sub = st.text_input("Subject")
        col1, col2, col3, col4 = st.columns(4)
        a_gr = col1.number_input("A Grade", 0)
        b_gr = col2.number_input("B Grade", 0)
        c_gr = col3.number_input("C Grade", 0)
        d_gr = col4.number_input("D Grade", 0)
        if st.form_submit_button("Save Record"):
            st.session_state.data_store["A"].append({"Class": s_class, "Subject": s_sub, "A": a_gr, "B": b_gr, "C": c_gr, "D": d_gr})
            st.rerun()
    display_key = "A"

elif nav == "Teacher Profiles (B)":
    st.header("👨‍🏫 Teacher Registration")
    with st.form("b_form"):
        t_name = st.text_input("Teacher Name")
        t_exp = st.text_input("Subject Expertise")
        t_rate = st.slider("Success Rate (%)", 1, 100, 70)
        if st.form_submit_button("Register Teacher"):
            st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_rate})
            st.rerun()
    display_key = "B"

elif nav == "Efficiency Mapping (C)":
    st.header("🎯 Resource Allocation")
    if not st.session_state.data_store["A"] or not st.session_state.data_store["B"]:
        st.warning("Complete Sections A & B first.")
    else:
        options = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
        sel = st.selectbox("Analyze Class", options)
        parts = sel.split(" | ")
        target = next(x for x in st.session_state.data_store["A"] if x['Class'] == parts[0] and x['Subject'] == parts[1])
        weak_factor = (target['C'] * 1.5) + (target['D'] * 2.5)
        matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == parts[1]]
        if matches:
            best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
            st.info(f"Recommended: {best_t['Name']} ({best_t['Success']}%)")
            if st.button("Confirm Deployment"):
                impact = min(200, (weak_factor * (best_t['Success']/40)))
                st.session_state.data_store["C"].append({"Class": parts[0], "Subject": parts[1], "Teacher": best_t['Name'], "Impact": round(impact, 2)})
                st.rerun()
    display_key = "C"

elif nav == "Institution Summary":
    st.header("🏫 Principal's Executive Dashboard")
    inst_name = st.text_input("Enter Institution Name", "Global Excellence Institute")
    if st.session_state.data_store["A"]:
        df_a = pd.DataFrame(st.session_state.data_store["A"])
        total_grades = df_a[['A', 'B', 'C', 'D']].sum().reset_index()
        total_grades.columns = ['Grade', 'Count']
        st.plotly_chart(px.bar(total_grades, x='Grade', y='Count', title="Overall Grade Distribution"))
        
        df_c = pd.DataFrame(st.session_state.data_store["C"]) if st.session_state.data_store["C"] else pd.DataFrame()
        if not df_c.empty:
            st.subheader("High Impact Deployments")
            st.table(df_c.sort_values(by='Impact', ascending=False))
        
        # --- NEW PDF BUTTON ---
        st.divider()
        if st.button("Generate Professional PDF"):
            pdf_data = export_pdf(df_a, df_c, inst_name)
            st.download_button("Download Report", pdf_data, f"{inst_name}_Report.pdf", "application/pdf")
    else:
        st.info("No data found.")
    display_key = None

# Shared View for Deletion
if 'display_key' in locals() and display_key and st.session_state.data_store[display_key]:
    st.divider()
    df = pd.DataFrame(st.session_state.data_store[display_key])
    st.dataframe(df, use_container_width=True)
    idx = st.selectbox("Select Row to Delete", df.index)
    if st.button("Delete Record"):
        st.session_state.data_store[display_key].pop(idx)
        st.rerun()
