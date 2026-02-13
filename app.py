import streamlit as st
import pandas as pd
from fpdf import FPDF

# --- 1. CORE INITIALIZATION ---
ACTIVATION_KEY = "PAK-2026"

if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'setup_complete' not in st.session_state: st.session_state.setup_complete = False
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Grades_Config": {},
        "A": [], # Student Performance
        "B": [], # Teachers
        "C": [], # Efficiency Mapping
        "School_Name": ""
    }

# --- 2. PDF ENGINE ---
class SchoolPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        name = st.session_state.data_store.get("School_Name", "SCHOOL REPORT")
        self.cell(0, 10, name.upper(), 0, 1, 'C')
        self.ln(5)

def create_pdf(data):
    pdf = SchoolPDF()
    pdf.add_page()
    df = pd.DataFrame(data)
    pdf.set_font('Arial', 'B', 10)
    if not df.empty:
        col_width = 190 / len(df.columns)
        for col in df.columns: pdf.cell(col_width, 10, str(col), 1)
        pdf.ln()
        pdf.set_font('Arial', '', 9)
        for _, row in df.iterrows():
            for val in row: pdf.cell(col_width, 10, str(val), 1)
            pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UPDATED BULK UPLOAD LOGIC ---
def handle_bulk_upload():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Excel Bulk Load")
    upload_type = st.sidebar.selectbox("Select Upload Type", ["Classes", "Student Performance", "Teachers"])
    uploaded_file = st.sidebar.file_uploader(f"Upload {upload_type} Excel", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            # Standardize headers: Strip spaces and capitalize everything
            df.columns = [str(c).strip().capitalize() for c in df.columns]

            if st.sidebar.button(f"Process {upload_type}"):
                if upload_type == "Student Performance":
                    # FIX: Forward fill empty 'Class' cells (handles the merged look in your screenshot)
                    if 'Class' in df.columns:
                        df['Class'] = df['Class'].ffill()
                    
                    required = ['Class', 'Subject', 'A', 'B', 'C', 'D']
                    # Check if standard columns exist
                    if all(col in df.columns for col in required):
                        # Ensure A, B, C, D are numbers
                        for col in ['A', 'B', 'C', 'D']:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                        
                        for _, row in df.iterrows():
                            # Only add if Subject is not empty
                            if pd.notna(row['Subject']):
                                st.session_state.data_store["A"].append({
                                    "Class": str(row['Class']), 
                                    "Subject": str(row['Subject']),
                                    "A": int(row['A']), "B": int(row['B']), 
                                    "C": int(row['C']), "D": int(row['D']),
                                    "Total": int(row['A']+row['B']+row['C']+row['D'])
                                })
                        st.sidebar.success(f"✅ {len(df)} Records Loaded!")
                    else:
                        st.sidebar.error(f"Columns must be: Class, Subject, A, B, C, D. Found: {list(df.columns)}")

                elif upload_type == "Classes":
                    for _, row in df.iterrows():
                        key = f"{row.get('Grade', 'N/A')}-{row.get('Section', 'X')}"
                        subs = [s.strip() for s in str(row.get('Subjects', '')).split(",")]
                        st.session_state.data_store["Grades_Config"][key] = subs
                    st.sidebar.success("Classes Loaded!")

                elif upload_type == "Teachers":
                    for _, row in df.iterrows():
                        st.session_state.data_store["B"].append({
                            "Name": row.get('Name', 'Unknown'), 
                            "Expertise": row.get('Expertise', 'N/A'), 
                            "Success": row.get('Success', 0)
                        })
                    st.sidebar.success("Teachers Loaded!")
                st.rerun()
        except Exception as e:
            st.sidebar.error(f"File Error: {e}")

# --- 4. UI LOGIC ---
if not st.session_state.authenticated:
    st.title("🔐 Secure Activation")
    key_input = st.text_input("Enter System Key", type="password")
    if st.button("Activate System"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Invalid Access Key")

elif not st.session_state.setup_complete:
    handle_bulk_upload()
    st.title("⚙️ School Configuration")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "My Institution")
    
    st.subheader("Step 1: Class Setup")
    c1, c2 = st.columns(2)
    g_name = c1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
    s_name = c2.text_input("Section (e.g., A)")
    sub_input = st.text_area("Subjects (comma separated)", "Math, Science")
    
    if st.button("Add Class"):
        if s_name:
            full_key = f"{g_name}-{s_name}"
            st.session_state.data_store["Grades_Config"][full_key] = [s.strip() for s in sub_input.split(",")]
            st.success(f"✅ Added {full_key}")
    
    if st.session_state.data_store["Grades_Config"]:
        if st.button("🚀 Finalize Setup"):
            st.session_state.setup_complete = True
            st.rerun()

else:
    st.sidebar.title(st.session_state.data_store["School_Name"])
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Navigation", ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    if nav == "Student Performance (A)":
        st.header("📊 Student Grades")
        # Display the table if data exists
        if st.session_state.data_store["A"]:
            df_display = pd.DataFrame(st.session_state.data_store["A"])
            st.dataframe(df_display, use_container_width=True)
            
            # Delete logic
            idx_to_del = st.selectbox("Select Row to Delete", df_display.index)
            if st.button("🗑️ Delete Row"):
                st.session_state.data_store["A"].pop(idx_to_del)
                st.rerun()

            pdf_b = create_pdf(st.session_state.data_store["A"])
            st.download_button("📥 Download Report", pdf_b, "Performance.pdf")
        
        # Manual Entry Form
        with st.expander("➕ Add Manual Entry"):
            class_list = list(st.session_state.data_store["Grades_Config"].keys())
            if class_list:
                sel_cl = st.selectbox("Class", class_list)
                sel_sb = st.selectbox("Subject", st.session_state.data_store["Grades_Config"][sel_cl])
                with st.form("man_a"):
                    c1, c2, c3, c4 = st.columns(4)
                    ga, gb = c1.number_input("A", 0), c2.number_input("B", 0)
                    gc, gd = c3.number_input("C", 0), c4.number_input("D", 0)
                    if st.form_submit_button("Save"):
                        st.session_state.data_store["A"].append({
                            "Class": sel_cl, "Subject": sel_sb, "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd
                        })
                        st.rerun()
            else: st.warning("No classes configured.")

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Teachers")
        if st.session_state.data_store["B"]:
            st.table(st.session_state.data_store["B"])
        
    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Recommendations")
        st.write("Data mapping active based on Section A and B.")
