import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Optimal Teacher-Student Resource Allocator", layout="wide")

# Mock Activation Key (In a real scenario, use Secrets)
ACTIVATION_KEY = "Ahsan123"

# --- SESSION STATE INITIALIZATION ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'org_name' not in st.session_state:
    st.session_state.org_name = ""
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Section A": 0.0, "Section B": 0.0, "Section C": 0.0, "Section D": 0.0
    }

# --- PDF GENERATION CLASS ---
class ReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Resource Allocation Analysis Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(org_name, scores, final_score):
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header Info
    pdf.cell(200, 10, txt=f"Organization: {org_name}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(10)
    
    # Data Table
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(100, 10, "Section", 1, 0, 'C', True)
    pdf.cell(90, 10, "Component Score", 1, 1, 'C', True)
    
    for section, val in scores.items():
        pdf.cell(100, 10, section, 1)
        pdf.cell(90, 10, f"{val:.2f}", 1, 1)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"FINAL AGGREGATE SCORE: {final_score}/200", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- UI LOGIC: ACTIVATION & IDENTITY ---
if not st.session_state.authenticated:
    st.title("🔐 System Activation")
    col1, col2 = st.columns(2)
    with col1:
        key_input = st.text_input("Enter Activation Key", type="password")
        org_input = st.text_input("Organization Name")
        
        if st.button("Activate System"):
            if key_input == ACTIVATION_KEY and org_input.strip() != "":
                st.session_state.authenticated = True
                st.session_state.org_name = org_input
                st.rerun()
            else:
                st.error("Invalid Key or Organization Name missing.")
    st.stop()

# --- MAIN APP INTERFACE ---
st.title(f"📊 {st.session_state.org_name}")
st.subheader("Optimal Teacher-Student Resource Allocator")

tabs = st.tabs(["Section A: Student Load", "Section B: Teacher Profile", 
                "Section C: Efficiency", "Section D: Feedback"])

# Generic function to handle data inputs
def handle_input(section_name, help_text):
    st.write(f"### {section_name} Data Entry")
    col_up, col_man = st.columns(2)
    
    with col_up:
        uploaded_file = st.file_uploader(f"Upload CSV/Excel for {section_name}", key=f"file_{section_name}")
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                st.success(f"Loaded {len(df)} rows")
                # Simplified logic: use mean of numeric columns as a factor
                return df.select_dtypes(include='number').mean().mean()
            except Exception as e:
                st.error(f"Error processing file: {e}")
                
    with col_man:
        val = st.number_input(f"Manual Entry Score (0-50) for {section_name}", 0.0, 50.0, 25.0, key=f"man_{section_name}")
        return val

# Tab Content
with tabs[0]:
    st.session_state.data_store["Section A"] = handle_input("Section A", "Grade-wise count and special needs.")

with tabs[1]:
    st.session_state.data_store["Section B"] = handle_input("Section B", "Qualification, seniority, performance.")

with tabs[2]:
    st.session_state.data_store["Section C"] = handle_input("Section C", "Ratios and admin task hours.")

with tabs[3]:
    st.session_state.data_store["Section D"] = handle_input("Section D", "Satisfaction and peer reviews.")

# --- FINAL CALCULATION & OUTPUT ---
st.divider()
st.header("Results Summary")

# Calculation Logic (Sum of sections, max 200)
final_score = sum(st.session_state.data_store.values())
# Ensure it stays within 1-200 bounds for the demo
final_score = max(1.0, min(200.0, final_score))

c1, c2 = st.columns(2)
with c1:
    st.metric("Aggregate Resource Score", f"{final_score:.2f} / 200")
    
with c2:
    pdf_data = generate_pdf(st.session_state.org_name, st.session_state.data_store, round(final_score, 2))
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_data,
        file_name=f"Resource_Report_{st.session_state.org_name}.pdf",
        mime="application/pdf"
    )

if st.button("🔄 Reset Application"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()
