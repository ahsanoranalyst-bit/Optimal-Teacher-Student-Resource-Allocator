

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# --- 1. SYSTEM CONFIGURATION ---
ACTIVATION_KEY = "PAK-2026"
EXPIRY_DATE = date(2026, 12, 31)

# Persistent State Management
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'school_name' not in st.session_state: st.session_state.school_name = ""
if 'store' not in st.session_state:
    st.session_state.store = {
        "A": [], "B": [], "C": [], "D": [], "Demands": []
    }

# --- 2. PROFESSIONAL PDF ENGINE ---
class ReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, st.session_state.school_name.upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"Resource Intelligence Report: {self.subtitle}", 0, 1, 'C')
        self.ln(5)
        self.line(10, 30, 200, 30)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Confidential | Generated: {datetime.now().strftime("%Y-%m-%d")} | Page {self.page_no()}', 0, 0, 'C')

def export_to_pdf(subtitle, data_list):
    pdf = ReportPDF()
    pdf.subtitle = subtitle
    pdf.add_page()
    if not data_list:
        pdf.cell(0, 10, "No data available.", 0, 1)
    else:
        df = pd.DataFrame(data_list)
        pdf.set_fill_color(200, 220, 255)
        pdf.set_font('Arial', 'B', 9)
        col_w = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(col_w, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        pdf.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            for val in row:
                pdf.cell(col_w, 9, str(val), 1)
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MULTI-STEP ACCESS CONTROL ---
if not st.session_state.authenticated:
    st.title("🔐 Enterprise System Access")
    key = st.text_input("Activation Key", type="password")
    if st.button("Unlock System", use_container_width=True):
        if key == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Invalid Key")

elif not st.session_state.setup_complete:
    st.title("🏫 Institution Initialization")
    name = st.text_input("Enter Registered School Name")
    if st.button("Configure Dashboard"):
        if name:
            st.session_state.school_name = name
            st.setup_complete = True
            st.rerun()

# --- 4. THE INTEGRATED CORE ---
else:
    st.sidebar.title(f"🏢 {st.session_state.school_name}")
    nav = st.sidebar.selectbox("Navigation", 
        ["Section A: Student Load", "Section B: Teacher Profiles", 
         "Section C: Efficiency Slots", "Section D: Feedback", 
         "Teacher Demands", "Smart Analysis Report"])
    
    if st.sidebar.button("System Logout"):
        st.session_state.authenticated = False
        st.rerun()

    st.title(nav)
    
    # --- LOGICAL SECTIONS ---

    if nav == "Section A: Student Load":
        with st.form("a_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            grade = c1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
            sec = c2.text_input("Section Name (e.g. A, B, Yellow)")
            tot = st.number_input("Total Enrollment", min_value=1)
            spec = st.number_input("Students with Special Needs", min_value=0)
            desc = st.text_area("Detail of Needs (Targeted Slot for Attention)")
            if st.form_submit_button("Record Class"):
                st.session_state.store["A"].append({"Grade": grade, "Section": sec, "Total": tot, "Special_Needs": spec, "Details": desc})
                st.rerun()
        current_data = st.session_state.store["A"]

    elif nav == "Section B: Teacher Profiles":
        with st.form("b_form", clear_on_submit=True):
            name = st.text_input("Teacher Name")
            qual = st.selectbox("Qualification", ["PhD", "Masters", "Bachelors"])
            exp = st.number_input("Experience (Years)", min_value=0)
            if st.form_submit_button("Save Profile"):
                st.session_state.store["B"].append({"Name": name, "Qual": qual, "Exp": exp})
                st.rerun()
        current_data = st.session_state.store["B"]

    elif nav == "Section C: Efficiency Slots":
        if not st.session_state.store["A"] or not st.session_state.store["B"]:
            st.warning("Please complete Section A and B first.")
        else:
            with st.form("c_form", clear_on_submit=True):
                t_list = [t['Name'] for t in st.session_state.store["B"]]
                c_list = [f"{c['Grade']}-{c['Section']}" for c in st.session_state.store["A"]]
                sel_t = st.selectbox("Select Teacher", t_list)
                sel_c = st.selectbox("Assign Class/Section", c_list)
                period = st.number_input("Periods per Week in this Class", min_value=1)
                adm = st.number_input("Admin/Desk Hours (Week)", value=1)
                if st.form_submit_button("Link Resource"):
                    st.session_state.store["C"].append({"Teacher": sel_t, "Class": sel_c, "Periods": period, "Admin": adm})
                    st.rerun()
        current_data = st.session_state.store["C"]

    elif nav == "Section D: Feedback":
        with st.form("d_form", clear_on_submit=True):
            src = st.selectbox("Source", ["Student", "Management", "Parent"])
            t_ref = st.text_input("Teacher Referenced")
            score = st.slider("Rating", 1, 10, 5)
            note = st.text_area("Feedback Note")
            if st.form_submit_button("Save Feedback"):
                st.session_state.store["D"].append({"Source": src, "Teacher": t_ref, "Rating": score, "Note": note})
                st.rerun()
        current_data = st.session_state.store["D"]

    elif nav == "Teacher Demands":
        with st.form("demand_f", clear_on_submit=True):
            who = st.text_input("Requested By")
            whom = st.text_input("Teacher Name")
            where = st.text_input("Target Section")
            if st.form_submit_button("Log Demand"):
                st.session_state.store["Demands"].append({"Requester": who, "Teacher": whom, "Target": where, "Date": str(date.today())})
                st.rerun()
        current_data = st.session_state.store["Demands"]

    elif nav == "Smart Analysis Report":
        analysis = []
        for row in st.session_state.store["C"]:
            # Logic: Load = (Periods * 5) + (Admin * 10) + (Special Needs * 5)
            cls_data = next((x for x in st.session_state.store["A"] if f"{x['Grade']}-{x['Section']}" == row['Class']), None)
            needs_weight = (cls_data['Special_Needs'] * 5) if cls_data else 0
            raw_score = (row['Periods'] * 5) + (row['Admin'] * 8) + needs_weight
            final_score = min(200, max(1, int(raw_score)))
            
            analysis.append({
                "Teacher": row['Teacher'], "Assigned": row['Class'], 
                "Load_Score": f"{final_score}/200", 
                "Status": "Balanced" if final_score < 150 else "High Burnout Risk"
            })
        st.subheader("Optimization Analysis Index")
        if analysis: st.table(analysis)
        current_data = analysis

    # --- UNIVERSAL PDF & TABLE VIEW ---
    if 'current_data' in locals() and current_data:
        st.markdown("---")
        st.dataframe(pd.DataFrame(current_data), use_container_width=True)
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Delete Last Entry"):
                # Logic to identify correct sub-store
                map_key = {"Section A": "A", "Section B": "B", "Section C": "C", "Section D": "D", "Teacher Demands": "Demands"}
                key = map_key.get(nav.split(":")[0], "Demands" if "Demands" in nav else "C")
                if st.session_state.store[key]:
                    st.session_state.store[key].pop()
                    st.rerun()
        with col_b:
            pdf_out = export_to_pdf(nav, current_data)
            st.download_button(f"Download {nav} PDF", pdf_out, f"{nav}.pdf", "application/pdf")
