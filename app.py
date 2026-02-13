


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
        "A": [],            
        "B": [],            
        "C": [],            
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

# --- 3. BULK UPLOAD LOGIC ---
def handle_bulk_upload():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Excel Bulk Load")
    upload_type = st.sidebar.selectbox("Select Upload Type", ["Classes", "Student Performance", "Teachers"])
    uploaded_file = st.sidebar.file_uploader(f"Upload {upload_type} Excel", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            if st.sidebar.button(f"Process {upload_type}"):
                if upload_type == "Classes":
                    for _, row in df.iterrows():
                        key = f"{row['Grade']}-{row['Section']}"
                        subs = [s.strip() for s in str(row['Subjects']).split(",")]
                        st.session_state.data_store["Grades_Config"][key] = subs
                    st.sidebar.success("Classes Loaded!")
               
                elif upload_type == "Student Performance":
                    for _, row in df.iterrows():
                        st.session_state.data_store["A"].append({
                            "Class": row['Class'], "Subject": row['Subject'],
                            "A": row['A'], "B": row['B'], "C": row['C'], "D": row['D'],
                            "Total": row['A']+row['B']+row['C']+row['D']
                        })
                    st.sidebar.success("Performance Data Loaded!")

                elif upload_type == "Teachers":
                    for _, row in df.iterrows():
                        st.session_state.data_store["B"].append({
                            "Name": row['Name'], "Expertise": row['Expertise'], "Success": row['Success']
                        })
                    st.sidebar.success("Teachers Loaded!")
                st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: Ensure columns match requirements.")

# --- 4. UI LOGIC ---

if not st.session_state.authenticated:
    st.title("🔐 Secure Activation")
    key_input = st.text_input("Enter System Key", type="password")
    if st.button("Activate System"):
        if key_input == ACTIVATION_KEY:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid Access Key")

elif not st.session_state.setup_complete:
    handle_bulk_upload()
    st.title("⚙️ School Configuration")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", st.session_state.data_store.get("School_Name", "My Institution"))
   
    st.subheader("Step 1: Define Grade, Section & Subjects")
    c1, c2 = st.columns(2)
    g_name = c1.selectbox("Grade", [f"Grade {i}" for i in range(1, 13)])
    s_name = c2.text_input("Section Name (e.g., A, B, Blue)")
   
    sub_input = st.text_area("Enter Subjects (separated by comma)", "Math, English, Science")
   
    if st.button("Add This Class Configuration"):
        if s_name:
            full_key = f"{g_name}-{s_name}"
            subjects = [s.strip() for s in sub_input.split(",") if s.strip()]
            st.session_state.data_store["Grades_Config"][full_key] = subjects
            st.success(f"✅ Added {full_key} successfully!")
        else:
            st.warning("⚠️ Please enter a Section name.")
   
    st.markdown("---")
    if st.session_state.data_store["Grades_Config"]:
        st.info(f"Total Classes Configured: {len(st.session_state.data_store['Grades_Config'])}")
        if st.button("🚀 Finalize & Go to Dashboard"):
            st.session_state.setup_complete = True
            st.rerun()

else:
    st.sidebar.title(st.session_state.data_store["School_Name"])
    handle_bulk_upload()
    nav = st.sidebar.selectbox("Main Navigation",
        ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)"])

    if nav == "Student Performance (A)":
        st.header("📊 Input Student Grades")
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        if not class_list:
            st.warning("No classes configured. Please use Bulk Upload or reset.")
        else:
            sel_class = st.selectbox("Select Class-Section", class_list)
            sel_sub = st.selectbox("Select Subject", st.session_state.data_store["Grades_Config"][sel_class])
           
            with st.form("a_form"):
                c1, c2, c3, c4 = st.columns(4)
                ga, gb, gc, gd = c1.number_input("A", 0), c2.number_input("B", 0), c3.number_input("C", 0), c4.number_input("D", 0)
                if st.form_submit_button("Save Performance Data"):
                    st.session_state.data_store["A"].append({
                        "Class": sel_class, "Subject": sel_sub,
                        "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd
                    })
                    st.rerun()
        display_key = "A"

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Teacher Specialization")
        all_subs = set()
        for s_list in st.session_state.data_store["Grades_Config"].values(): all_subs.update(s_list)
       
        with st.form("b_form"):
            t_name = st.text_input("Full Name")
            t_exp = st.selectbox("Specialized Subject", list(all_subs) if all_subs else ["N/A"])
            t_rate = st.slider("Historical Success Rate (%)", 1, 100, 70)
            if st.form_submit_button("Register Teacher"):
                st.session_state.data_store["B"].append({"Name": t_name, "Expertise": t_exp, "Success": t_rate})
                st.rerun()
        display_key = "B"

    elif nav == "Efficiency Mapping (C)":
        st.header("🎯 Solid Evidence & Allocation")
        if not st.session_state.data_store["A"] or not st.session_state.data_store["B"]:
            st.warning("Please complete Section A and B first.")
        else:
            options = [f"{x['Class']} | {x['Subject']}" for x in st.session_state.data_store["A"]]
            sel = st.selectbox("Select Class/Subject to Analyze", options)
            parts = sel.split(" | ")
            target_data = next(x for x in st.session_state.data_store["A"] if x['Class'] == parts[0] and x['Subject'] == parts[1])
           
            weak_factor = (target_data['C'] * 1.5) + (target_data['D'] * 2.5)
            matches = [t for t in st.session_state.data_store["B"] if t['Expertise'] == parts[1]]
           
            if matches:
                best_t = sorted(matches, key=lambda x: x['Success'], reverse=True)[0]
                assigned_classes = [c['Class'] for c in st.session_state.data_store["C"] if c['Teacher'] == best_t['Name']]
                workload_count = len(assigned_classes)
               
                st.info(f"💡 Recommendation: **{best_t['Name']}** (Score: {best_t['Success']}%)")
                st.write(f"📌 Current Workload: Assigned to **{workload_count}** classes.")
                if st.button("Confirm Deployment"):
                    impact = min(200, (weak_factor * (best_t['Success']/40)))
                    st.session_state.data_store["C"].append({
                        "Class": parts[0], "Subject": parts[1], "Teacher": best_t['Name'], "Impact": round(impact, 2)
                    })
                    st.rerun()
            else:
                st.error("No specialized teacher found.")
        display_key = "C"

    # --- SHARED VIEW ---
    if 'display_key' in locals() and st.session_state.data_store[display_key]:
        st.markdown("---")
        df = pd.DataFrame(st.session_state.data_store[display_key])
        st.dataframe(df, use_container_width=True)
        idx = st.selectbox("Select Row to Delete", df.index)
        if st.button("🗑️ Delete"):
            st.session_state.data_store[display_key].pop(idx)
            st.rerun()
        pdf_bytes = create_pdf(st.session_state.data_store[display_key])
        st.download_button("📥 Download PDF", pdf_bytes, f"{nav}.pdf")
