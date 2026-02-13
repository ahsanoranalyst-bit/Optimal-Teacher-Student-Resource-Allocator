import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Optimal Teacher-Student Resource Allocator", layout="wide")

def initialize_session():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'org_name' not in st.session_state:
        st.session_state.org_name = ""
    if 'data' not in st.session_state:
        st.session_state.data = {
            "Section A": pd.DataFrame(),
            "Section B": pd.DataFrame(),
            "Section C": pd.DataFrame(),
            "Section D": pd.DataFrame()
        }

initialize_session()

# --- PDF GENERATION LOGIC ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f'Resource Allocation Report - {st.session_state.org_name}', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(score, summary_data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Final Allocation Score: {score}/200", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    for section, details in summary_data.items():
        pdf.cell(200, 10, txt=f"{section}:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 10, txt=details)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 1. MULTI-LEVEL ENTRY (GATING) ---
if not st.session_state.authenticated:
    st.title("🔐 System Activation")
    col1, col2 = st.columns(2)
    
    with col1:
        activation_key = st.text_input("Enter Activation Key", type="password")
        org_input = st.text_input("Organization Name")
        
        if st.button("Activate System"):
            # Hardcoded key for internal use; in prod, use st.secrets
            if activation_key == "Ahsan123": 
                if org_input:
                    st.session_state.authenticated = True
                    st.session_state.org_name = org_input
                    st.rerun()
                else:
                    st.error("Please enter an Organization Name.")
            else:
                st.error("Invalid Activation Key.")
    st.stop()

# --- MAIN APP INTERFACE ---
st.title(f"📊 {st.session_state.org_name}")
st.subheader("Optimal Teacher-Student Resource Allocator")

# --- 2. SECTION-WISE ARCHITECTURE (TABS) ---
tab_a, tab_b, tab_c, tab_d, tab_out = st.tabs([
    "Section A: Student Load", 
    "Section B: Teacher Profile", 
    "Section C: Efficiency", 
    "Section D: Feedback",
    "Final Results"
])

sections = {
    "Section A": "Grade-wise student count, Special needs students",
    "Section B": "Qualification, Seniority, Past performance metrics",
    "Section C": "Target Teacher-Student ratio, Admin task hours",
    "Section D": "Student satisfaction scores, Peer review data"
}

def handle_data_input(section_key, description):
    st.info(f"Data Focus: {description}")
    
    upload = st.file_uploader(f"Upload CSV/Excel for {section_key}", type=['csv', 'xlsx'], key=f"up_{section_key}")
    
    if upload:
        try:
            df = pd.read_csv(upload) if upload.name.endswith('.csv') else pd.read_excel(upload)
            st.session_state.data[section_key] = df
            st.success(f"Loaded {len(df)} rows.")
        except Exception as e:
            st.error(f"Error loading file: {e}")
            
    # Manual Entry fallback/view
    with st.expander("Manual Data Entry / Preview"):
        edited_df = st.data_editor(st.session_state.data[section_key], num_rows="dynamic", key=f"ed_{section_key}")
        st.session_state.data[section_key] = edited_df

with tab_a: handle_data_input("Section A", sections["Section A"])
with tab_b: handle_data_input("Section B", sections["Section B"])
with tab_c: handle_data_input("Section C", sections["Section C"])
with tab_d: handle_data_input("Section D", sections["Section D"])

# --- 3. OUTPUT & MATHEMATICAL CALCULATION ---
with tab_out:
    st.header("Resource Allocation Summary")
    
    # Simple logic to simulate calculation based on data presence
    # In a real app, replace with complex math: e.g., df['score'].mean()
    base_score = 0
    summary_text = {}
    
    for sec in sections.keys():
        rows = len(st.session_state.data[sec])
        val = min(rows * 10, 50) # Cap each section at 50 pts for demo
        base_score += val
        summary_text[sec] = f"Processed {rows} data entries. Section Contribution: {val}/50."

    final_score = min(base_score, 200)
    
    col_score, col_btn = st.columns(2)
    with col_score:
        st.metric("Final Allocation Score", f"{final_score} / 200")
    
    # PDF Export
    pdf_bytes = generate_pdf(final_score, summary_text)
    
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_bytes,
        file_name=f"Allocation_Report_{st.session_state.org_name}.pdf",
        mime="application/pdf"
    )

    st.divider()
    if st.button("🔄 Reload Application"):
        st.session_state.clear()
        st.rerun()
