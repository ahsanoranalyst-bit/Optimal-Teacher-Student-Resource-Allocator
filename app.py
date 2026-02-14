import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. CORE INITIALIZATION ---
ACTIVATION_KEY = "PAK-2026"

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Grades_Config": {},
        "A": [], "B": [], "C": [],
        "School_Name": ""
    }

# --- 2. PROFESSIONAL PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 73, 125) 
        self.rect(0, 0, 210, 35, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        name = str(st.session_state.data_store.get("School_Name", "INSTITUTION")).upper()
        self.cell(0, 12, name, 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, "OFFICIAL ACADEMIC PERFORMANCE REPORT", 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-30)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "__________________________", 0, 1, 'R')
        self.cell(0, 5, "Authorized Signature & Stamp", 0, 1, 'R')
        ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.cell(0, 10, f"Date: {ts} | Page {self.page_no()}", 0, 0, 'L')

def clean_val(val):
    """Returns empty string if value is None or NaN"""
    if pd.isna(val) or val is None or str(val).lower() in ['nan', 'none']:
        return ""
    return str(val).strip()

def create_pdf(data, title):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 10, f"SECTION: {title.upper()}", 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    if not df.empty:
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(230, 235, 245)
        col_w = 190 / len(df.columns)
        for col in df.columns:
            pdf.cell(col_w, 10, str(col), 1, 0, 'C', True)
        pdf.ln()
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(0, 0, 0)
        for _, row in df.iterrows():
            for val in row:
                pdf.cell(col_w, 9, clean_val(val), 1, 0, 'C')
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. BULK UPLOAD LOGIC ---
def handle_bulk_upload():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Bulk Import")
    cat = st.sidebar.selectbox("File Category", ["Classes", "Performance", "Teachers"], key="cat")
    file = st.sidebar.file_uploader(f"Upload {cat} Excel", type=["xlsx"], key="f_up")

    if file and st.sidebar.button("Confirm Import"):
        try:
            # ffill() fixes the "None" error for merged/blank cells in Excel
            df = pd.read_excel(file).ffill().fillna('')
            df.columns = [str(c).strip() for c in df.columns]
            
            if cat == "Classes":
                for _, row in df.iterrows():
                    k = f"{row['Grade']}-{row['Section']}"
                    s = [x.strip() for x in str(row['Subjects']).split(",") if x.strip()]
                    st.session_state.data_store["Grades_Config"][k] = s
            
            elif cat == "Performance":
                for _, row in df.iterrows():
                    a, b, c, d = [int(row[x]) if str(row[x]).isdigit() else 0 for x in ['A', 'B', 'C', 'D']]
                    st.session_state.data_store["A"].append({
                        "Class": str(row['Class']), "Subject": str(row['Subject']),
                        "A": a, "B": b, "C": c, "D": d, "Total": a+b+c+d
                    })

            elif cat == "Teachers":
                for _, row in df.iterrows():
                    st.session_state.data_store["B"].append({
                        "Name": str(row['Name']), "Expertise": str(row['Expertise']), 
                        "Success": row['Success']
                    })
            st.sidebar.success("Imported Successfully!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# --- 4. NAVIGATION ---
if not st.session_state.authenticated:
    st.title("🔐 Login")
    if st.text_input("System Key", type="password") == ACTIVATION_KEY:
        if st.button("Access"):
            st.session_state.authenticated = True
            st.rerun()

elif not st.session_state.setup_complete:
    st.title("⚙️ Setup")
    handle_bulk_upload()
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "Global Academy")
    if st.button("Enter Dashboard") and st.session_state.data_store["Grades_Config"]:
        st.session_state.setup_complete = True
        st.rerun()
    elif not st.session_state.data_store["Grades_Config"]:
        st.warning("Please upload or add at least one class first.")

else:
    st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    handle_bulk_upload()
    menu = st.sidebar.selectbox("Menu", ["Student Performance", "Teacher Experts", "Efficiency Strategy"])
    
    key_map = {"Student Performance": "A", "Teacher Experts": "B", "Efficiency Strategy": "C"}
    current_key = key_map[menu]

    if current_key == "A":
        st.header("📊 Performance Data")
        with st.expander("Manual Add"):
            cls_list = list(st.session_state.data_store["Grades_Config"].keys())
            if cls_list:
                sel_c = st.selectbox("Class", cls_list)
                sel_s = st.selectbox("Subject", st.session_state.data_store["Grades_Config"][sel_c])
                c1,c2,c3,c4 = st.columns(4)
                vA,vB,vC,vD = c1.number_input("A",0), c2.number_input("B",0), c3.number_input("C",0), c4.number_input("D",0)
                if st.button("Save"):
                    st.session_state.data_store["A"].append({"Class": sel_c, "Subject": sel_s, "A": vA, "B": vB, "C": vC, "D": vD, "Total": vA+vB+vC+vD})
                    st.rerun()

    elif current_key == "B":
        st.header("👨‍🏫 Faculty Experts")
        with st.form("t_form"):
            n, ex, sc = st.text_input("Name"), st.text_input("Expertise"), st.slider("Success %", 0,100, 80)
            if st.form_submit_button("Add Teacher"):
                st.session_state.data_store["B"].append({"Name": n, "Expertise": ex, "Success": sc})
                st.rerun()

    elif current_key == "C":
        st.header("🎯 Deployment Strategy")
        if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
            perf_df = pd.DataFrame(st.session_state.data_store["A"])
            target = st.selectbox("Select Target", [f"{r['Class']} | {r['Subject']}" for _, r in perf_df.iterrows()])
            if st.button("Match Teacher"):
                subj = target.split(" | ")[1]
                matches = [t for t in st.session_state.data_store["B"] if t['Expertise'].lower() == subj.lower()]
                if matches:
                    best = max(matches, key=lambda x: x['Success'])
                    st.session_state.data_store["C"].append({"Target": target, "Assigned": best['Name'], "Status": "OPTIMIZED"})
                    st.success(f"Assigned {best['Name']}")
                    st.rerun()

    # Table Display
    if st.session_state.data_store[current_key]:
        st.divider()
        df_view = pd.DataFrame(st.session_state.data_store[current_key])
        st.dataframe(df_view, use_container_width=True)
        
        col_del, col_pdf = st.columns(2)
        with col_del:
            idx = st.number_input("Row Index", 0, max(0, len(df_view)-1), 0)
            if st.button("🗑️ Delete"):
                st.session_state.data_store[current_key].pop(idx)
                st.rerun()
        with col_pdf:
            pdf_bytes = create_pdf(st.session_state.data_store[current_key], menu)
            st.download_button("📥 Download PDF", pdf_bytes, f"{menu}_Report.pdf")
