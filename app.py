import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. CORE INITIALIZATION ---
ACTIVATION_KEY = "PAK-2026"

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Grades_Config": {},
        "A": [], "B": [], "C": [],
        "School_Name": "Global International Academy"
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
        for _, row in df.iterrows():
            for val in row:
                pdf.cell(col_w, 9, clean_val(val), 1, 0, 'C')
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. BULK UPLOAD LOGIC ---
def handle_bulk_upload():
    st.sidebar.markdown("### 📂 Data Management")
    cat = st.sidebar.selectbox("File Category", ["Classes", "Performance", "Teachers"], key="cat")
    file = st.sidebar.file_uploader(f"Upload {cat} Excel", type=["xlsx"], key="f_up")

    if file and st.sidebar.button("Confirm & Sync Data"):
        try:
            # ffill() ensures Grade names are carried down to avoid "None"
            df = pd.read_excel(file).ffill().fillna('')
            df.columns = [str(c).strip() for c in df.columns]
            
            if cat == "Classes":
                st.session_state.data_store["Grades_Config"] = {} # Reset old config
                for _, row in df.iterrows():
                    k = f"{row['Grade']}-{row['Section']}"
                    s = [x.strip() for x in str(row['Subjects']).split(",") if x.strip()]
                    st.session_state.data_store["Grades_Config"][k] = s
            
            elif cat == "Performance":
                st.session_state.data_store["A"] = [] # Clear old data
                for _, row in df.iterrows():
                    a, b, c, d = [int(row[x]) if str(row[x]).isdigit() else 0 for x in ['A', 'B', 'C', 'D']]
                    st.session_state.data_store["A"].append({
                        "Class": str(row['Class']), "Subject": str(row['Subject']),
                        "A": a, "B": b, "C": c, "D": d, "Total": a+b+c+d
                    })

            elif cat == "Teachers":
                st.session_state.data_store["B"] = [] # Clear old data
                for _, row in df.iterrows():
                    st.session_state.data_store["B"].append({
                        "Name": str(row['Name']), "Expertise": str(row['Expertise']), 
                        "Success": row['Success']
                    })
            st.sidebar.success(f"{cat} Updated!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# --- 4. MAIN INTERFACE ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Login")
    if st.text_input("System Key", type="password") == ACTIVATION_KEY:
        if st.button("Unlock Dashboard"):
            st.session_state.authenticated = True
            st.rerun()

else:
    # Header with School Name Edit Option
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title(f"🏫 {st.session_state.data_store['School_Name']}")
    with col_h2:
        new_name = st.text_input("Change School Name", value=st.session_state.data_store['School_Name'])
        if new_name != st.session_state.data_store['School_Name']:
            st.session_state.data_store['School_Name'] = new_name
            st.rerun()

    handle_bulk_upload()
    
    menu = st.sidebar.selectbox("Main Menu", ["Student Records", "Teacher Records", "Strategy Mapping"])
    
    # Map menu to data key
    d_key = "A" if "Student" in menu else "B" if "Teacher" in menu else "C"

    if d_key == "C":
        st.header("🎯 Deployment Strategy")
        if st.session_state.data_store["A"] and st.session_state.data_store["B"]:
            perf_df = pd.DataFrame(st.session_state.data_store["A"])
            target = st.selectbox("Analyze Needs for:", [f"{r['Class']} | {r['Subject']}" for _, r in perf_df.iterrows()])
            if st.button("Generate Strategy"):
                subj = target.split(" | ")[1]
                matches = [t for t in st.session_state.data_store["B"] if str(t['Expertise']).lower() == subj.lower()]
                if matches:
                    best = max(matches, key=lambda x: x['Success'])
                    st.session_state.data_store["C"].append({"Target": target, "Assigned": best['Name'], "Success_Score": best['Success'], "Status": "OPTIMIZED"})
                    st.rerun()
                else:
                    st.warning("No teacher matching this expertise found.")

    # Show Data Table
    if st.session_state.data_store[d_key]:
        st.subheader(f"📋 {menu}")
        df_view = pd.DataFrame(st.session_state.data_store[d_key])
        st.dataframe(df_view, use_container_width=True)
        
        # Actions
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Clear This Table"):
                st.session_state.data_store[d_key] = []
                st.rerun()
        with c2:
            pdf_bytes = create_pdf(st.session_state.data_store[d_key], menu)
            st.download_button("📥 Download PDF Report", pdf_bytes, f"{menu}_Report.pdf")
    else:
        st.info(f"No data available for {menu}. Please upload the relevant Excel file in the sidebar.")
