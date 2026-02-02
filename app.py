import streamlit as st
import pandas as pd
from fpdf import FPDF
import plotly.express as px
import io
import tempfile
import os

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

# --- 3. UI LOGIC ---
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
    st.title("⚙️ School Configuration")
    st.session_state.data_store["School_Name"] = st.text_input("School Name", "My Institution")
    
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
    nav = st.sidebar.selectbox("Main Navigation", 
        ["Student Performance (A)", "Teacher Experts (B)", "Efficiency Mapping (C)", "Institution Summary"])

    if nav == "Student Performance (A)":
        st.header("📊 Input Student Grades")
        class_list = list(st.session_state.data_store["Grades_Config"].keys())
        sel_class = st.selectbox("Select Class-Section", class_list)
        sel_sub = st.selectbox("Select Subject", st.session_state.data_store["Grades_Config"][sel_class])
        
        with st.form("a_form"):
            c1, c2, c3, c4 = st.columns(4)
            ga, gb, gc, gd = c1.number_input("A", 0), c2.number_input("B", 0), c3.number_input("C", 0), c4.number_input("D", 0)
            if st.form_submit_button("Save Performance Data"):
                st.session_state.data_store["A"].append({"Class": sel_class, "Subject": sel_sub, "A": ga, "B": gb, "C": gc, "D": gd, "Total": ga+gb+gc+gd})
                st.rerun()
        display_key = "A"

    elif nav == "Teacher Experts (B)":
        st.header("👨‍🏫 Teacher Specialization")
        all_subs = set()
        for s_list in st.session_state.data_store["Grades_Config"].values(): all_subs.update(s_list)
        
        with st.form("b_form"):
            t_name = st.text_input("Full Name")
            t_exp = st.selectbox("Specialized Subject", list(all_subs))
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
                assigned_classes = [c['Class'] for c in st.session_state.data_store["C"] if 'Teacher' in c and c['Teacher'] == best_t['Name']]
                
                st.info(f"💡 Recommendation: **{best_t['Name']}** (Score: {best_t['Success']}%)")
                st.write(f"📌 Workload: Assigned to **{len(assigned_classes)}** classes.")

                if st.button("Confirm Deployment"):
                    impact = min(200, (weak_factor * (best_t['Success']/40)))
                    st.session_state.data_store["C"].append({"Class": parts[0], "Subject": parts[1], "Teacher": best_t['Name'], "Impact": round(impact, 2)})
                    st.rerun()
        display_key = "C"

    elif nav == "Institution Summary":
        st.header("🏫 Principal's Executive Dashboard")
        if st.session_state.data_store["A"]:
            df_a = pd.DataFrame(st.session_state.data_store["A"])
            
            # 1. Charts for Display
            total_grades = df_a[['A', 'B', 'C', 'D']].sum().reset_index()
            total_grades.columns = ['Grade', 'Count']
            fig_grades = px.bar(total_grades, x='Grade', y='Count', title="Overall School Grade Distribution", color='Grade')
            st.plotly_chart(fig_grades)
            
            df_a['Weakness'] = df_a['C'] + df_a['D']
            fig_weak = px.pie(df_a, values='Weakness', names='Subject', title="Weakest Areas by Subject")
            st.plotly_chart(fig_weak)
            
            st.markdown("---")
            # --- NEW PDF GENERATION SECTION ---
            if st.button("📥 Generate Institution Report (PDF)"):
                with st.spinner("Preparing Report..."):
                    try:
                        pdf = SchoolPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", 'B', 14)
                        pdf.cell(0, 10, "Institution Performance Summary", 0, 1, 'L')
                        pdf.ln(5)

                        # Logic to save Plotly figures to images
                        # Using Kaleido engine for high compatibility
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp1:
                            fig_grades.write_image(tmp1.name, engine="kaleido")
                            pdf.image(tmp1.name, x=10, y=None, w=180)
                            tmp1_path = tmp1.name

                        pdf.ln(10)

                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp2:
                            fig_weak.write_image(tmp2.name, engine="kaleido")
                            pdf.image(tmp2.name, x=10, y=None, w=180)
                            tmp2_path = tmp2.name

                        # Output PDF bytes
                        pdf_output = pdf.output(dest='S').encode('latin-1')
                        st.download_button(
                            label="📥 Download PDF Now",
                            data=pdf_output,
                            file_name="Institution_Report.pdf",
                            mime="application/pdf"
                        )
                        st.success("Report Ready!")
                        
                        # Cleanup temp files
                        os.remove(tmp1_path)
                        os.remove(tmp2_path)
                        
                    except Exception as e:
                        st.error(f"PDF Error: {str(e)}")
                        st.info("Check if 'kaleido' and 'fpdf' are in your requirements.txt")

            if st.session_state.data_store["C"]:
                df_c = pd.DataFrame(st.session_state.data_store["C"])
                st.subheader("Top Performing Deployments")
                st.table(df_c.sort_values(by='Impact', ascending=False).head(5))
        else:
            st.info("No data available for summary yet.")
        display_key = None

    # --- SHARED VIEW ---
    if 'display_key' in locals() and display_key and st.session_state.data_store[display_key]:
        st.markdown("---")
        df = pd.DataFrame(st.session_state.data_store[display_key])
        st.dataframe(df, use_container_width=True)
        idx = st.selectbox("Select Row to Delete", df.index)
        if st.button("🗑️ Delete Record"):
            st.session_state.data_store[display_key].pop(idx)
            st.rerun()
