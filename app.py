import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date
import io

# --- 1. SETTINGS & LICENSE ---
ACTIVATION_KEY = "PAK-2026"
EXPIRY_DATE = date(2026, 12, 31)

# Initialize Session States
if 'auth' not in st.session_state: st.session_state.auth = False
if 'setup' not in st.session_state: st.session_state.setup = False
if 'school_name' not in st.session_state: st.session_state.school_name = ""
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Classes": [], "Teachers": [], "Efficiency": [], "Feedback": [], "Demands": []
    }

# --- 2. MULTI-PURPOSE PDF ENGINE ---
class MasterPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, st.session_state.school_name.upper(), 0, 1, 'C')
        self.set_font('Arial', 'I', 11)
        self.cell(0, 10, f"Official Report: {self.report_title}", 0, 1, 'C')
        self.ln(10)
        self.line(10, 32, 200, 32)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d")} | Page {self.page_no()}', 0, 0, 'C')

def generate_report(title, data_list):
    pdf = MasterPDF()
    pdf.report_title = title
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    if not data_list:
        pdf.cell(0, 10, "No data records available for this section.", 0, 1)
    else:
        df = pd.DataFrame(data_list)
        # Create Headers
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", 'B', 10)
        col_width = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(col_width, 10, str(col), 1, 0, 'C', fill=True)
        pdf.ln()
        
        # Create Rows
        pdf.set_font("Arial", '', 9)
        for _, row in df.iterrows():
            for item in row:
                pdf.cell(col_width, 10, str(item), 1)
            pdf.ln()
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. ACCESS CONTROL FLOW ---
if not st.session_state.auth:
    st.title("🔐 System Activation")
    key = st.text_input("Enter License Key", type="password")
    if st.button("Activate"):
        if key == ACTIVATION_KEY:
            st.session_state.auth = True
            st.rerun()
        else: st.error("Invalid License Key")

elif not st.session_state.setup:
    st.title("🏫 Institution Setup")
    sn = st.text_input("Enter School/Institution Name")
    if st.button("Initialize Dashboard"):
        if sn:
            st.session_state.school_name = sn
            st.session_state.setup = True
            st.rerun()

# --- 4. MAIN DASHBOARD ---
else:
    st.sidebar.title(f"🏢 {st.session_state.school_name}")
    menu = st.sidebar.selectbox("Main Navigation", 
        ["Section A: Student Load", "Section B: Teacher Profile", 
         "Section C: Efficiency", "Section D: Feedback", 
         "Teacher Demands", "Smart Analysis Report"])
    
    if st.sidebar.button("Logout"):
        st.session_state.auth = False; st.session_state.setup = False
        st.rerun()

    st.title(menu)

    # --- SECTION LOGIC (A, B, C, D, Demands) ---
    
    # SECTION A: CLASSES
    if menu == "Section A: Student Load":
        with st.form("a_form", clear_on_submit=True):
            g = st.selectbox("Grade", [f"Grade {i}" for i in range(1,13)])
            s = st.text_input("Section Name (e.g., A, B, Blue)")
            stds = st.number_input("Students Count", min_value=1)
            if st.form_submit_button("Save Class"):
                st.session_state.data_store["Classes"].append({"Grade": g, "Section": s, "Students": stds})
                st.rerun()
        data_to_show = st.session_state.data_store["Classes"]

    # SECTION B: TEACHERS
    elif menu == "Section B: Teacher Profile":
        with st.form("b_form", clear_on_submit=True):
            t = st.text_input("Teacher Name")
            e = st.number_input("Years of Experience", min_value=0)
            if st.form_submit_button("Add Teacher"):
                st.session_state.data_store["Teachers"].append({"Teacher": t, "Experience": e})
                st.rerun()
        data_to_show = st.session_state.data_store["Teachers"]

    # SECTION C: EFFICIENCY (Linking Class + Teacher)
    elif menu == "Section C: Efficiency":
        if not st.session_state.data_store["Teachers"]: st.warning("Add Teachers in Section B first.")
        else:
            with st.form("c_form", clear_on_submit=True):
                t_list = [t['Teacher'] for t in st.session_state.data_store["Teachers"]]
                c_list = [f"{c['Grade']}-{c['Section']}" for c in st.session_state.data_store["Classes"]]
                sel_t = st.selectbox("Select Teacher", t_list)
                sel_c = st.selectbox("Assign to Class", c_list)
                p = st.number_input("Periods per Week", min_value=1)
                adm = st.number_input("Admin Hours (per week)", value=1)
                if st.form_submit_button("Link Schedule"):
                    st.session_state.data_store["Efficiency"].append({"Teacher": sel_t, "Class": sel_c, "Periods": p, "Admin": adm})
                    st.rerun()
        data_to_show = st.session_state.data_store["Efficiency"]

    # TEACHER DEMANDS
    elif menu == "Teacher Demands":
        with st.form("demand_form", clear_on_submit=True):
            req = st.text_input("Requested By")
            t_req = st.text_input("Teacher Requested")
            target = st.text_input("Target Section")
            if st.form_submit_button("Submit Demand"):
                st.session_state.data_store["Demands"].append({"By": req, "Teacher": t_req, "Target": target})
                st.rerun()
        data_to_show = st.session_state.data_store["Demands"]

    # SMART ANALYSIS (AI Logic + Full PDF)
    elif menu == "Smart Analysis Report":
        st.subheader("Automated Resource Optimization Index")
        analysis_data = []
        for eff in st.session_state.data_store["Efficiency"]:
            # Basic Score Logic (1-200)
            score = min(200, (eff['Periods'] * 4) + (eff['Admin'] * 10))
            analysis_data.append({"Teacher": eff['Teacher'], "Class": eff['Class'], "Workload Score": f"{score}/200", "Status": "Optimized" if score < 150 else "Overloaded"})
        
        st.table(analysis_data)
        data_to_show = analysis_data

    # SECTION D: FEEDBACK (Simplified for this version)
    else:
        with st.form("d_form"):
            t_f = st.text_input("Teacher Name")
            f_b = st.slider("Rating", 1, 10)
            if st.form_submit_button("Save Feedback"):
                st.session_state.data_store["Feedback"].append({"Teacher": t_f, "Rating": f_b})
        data_to_show = st.session_state.data_store["Feedback"]

    # --- SHARED VIEW & PDF DOWNLOAD ---
    if data_to_show:
        st.markdown("---")
        st.dataframe(pd.DataFrame(data_to_show), use_container_width=True)
        
        # Row deletion logic
        idx = st.number_input("Enter Row ID to Delete", 0, len(data_to_show)-1, 0)
        if st.button("Delete Record"):
            # Logic to find correct list and pop
            key_map = {"Section A": "Classes", "Section B": "Teachers", "Section C": "Efficiency", "Teacher Demands": "Demands", "Section D": "Feedback"}
            key = key_map.get(menu.split(":")[0], menu)
            if key in st.session_state.data_store:
                st.session_state.data_store[key].pop(idx)
                st.rerun()

        # PDF Export for the current section
        if st.button(f"📥 Export {menu} as PDF"):
            pdf_bytes = generate_report(menu, data_to_show)
            st.download_button("Download Now", pdf_bytes, f"{menu.replace(':', '')}.pdf")
