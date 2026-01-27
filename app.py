import streamlit as st
import pandas as pd
import numpy as np

class ResourceAllocator:
    def __init__(self, total_students, sn_pct, target_ratio, admin_hours):
        self.total_students = total_students
        self.sn_pct = sn_pct
        self.target_ratio = target_ratio
        self.admin_hours = admin_hours

    def calculate_load(self):
        """Calculates the weighted student load based on Section A."""
        sn_count = self.total_students * (self.sn_pct / 100)
        gen_count = self.total_students - sn_count
        # Special needs students weighted at 2.0x resource requirement
        weighted_load = gen_count + (sn_count * 2.0)
        return gen_count, sn_count, weighted_load

    def get_staffing_needs(self, weighted_load):
        """Calculates staffing requirements based on Section C."""
        standard_need = int(np.ceil(self.total_students / self.target_ratio))
        optimized_need = int(np.ceil(weighted_load / self.target_ratio))
        return standard_need, optimized_need

    @staticmethod
    def rank_teachers(df):
        """Processes Section B & D to find the best resource fits."""
        # Creating a Composite Score: 40% Performance, 30% Satisfaction, 20% Peer, 10% Seniority
        df['Composite Score'] = (
            (df['Performance'] * 4) + 
            (df['Satisfaction'] / 10 * 3) + 
            (df['Peer Review'] * 2) +
            (df['Seniority'] * 0.1)
        ) / 10
        return df.sort_values(by='Composite Score', ascending=False)

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Optimal Resource Allocator", layout="wide")
st.title("⚖️ Optimal Teacher-Student Resource Allocator")

# --- SIDEBAR (Sections A & C) ---
with st.sidebar:
    st.header("Section A: Student Load")
    total_students = st.number_input("Total Student Population", 100, 5000, 800)
    sn_pct = st.slider("Special Needs Students (%)", 0, 50, 15)
    
    st.header("Section C: Efficiency")
    target_ratio = st.slider("Target Ratio (Students per Teacher)", 10, 40, 22)
    admin_hours = st.number_input("Weekly Admin Hours", 0, 20, 4)

# --- DATA INITIALIZATION (Sections B & D) ---
# In a real app, this would be a file upload (CSV/Excel)
teacher_data = pd.DataFrame({
    "Teacher Name": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
    "Qualification": ["Masters", "Bachelors", "PhD", "Masters", "Bachelors"],
    "Seniority": [10, 3, 15, 7, 2],
    "Performance": [9.0, 7.5, 9.5, 8.2, 6.8],
    "Satisfaction": [92, 85, 96, 88, 79],
    "Peer Review": [4.8, 3.2, 4.9, 4.1, 3.0]
})

# --- EXECUTION ---
allocator = ResourceAllocator(total_students, sn_pct, target_ratio, admin_hours)
gen, sn, weighted = allocator.calculate_load()
std_need, opt_need = allocator.get_staffing_needs(weighted)

# --- DISPLAY ---
t1, t2 = st.tabs(["📈 Allocation Logic", "🧑‍🏫 Teacher Merit Analysis"])

with t1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Raw Student Count", int(total_students))
    col2.metric("Weighted Load", f"{weighted:.1f}", help="Adjusted for Special Needs intensity")
    col3.metric("Required Staff", opt_need, delta=int(opt_need - std_need))

    st.subheader("Resource Distribution")
    chart_data = pd.DataFrame({
        "Type": ["General Ed", "Special Ed Support"],
        "Students": [gen, sn]
    })
    st.bar_chart(chart_data.set_index("Type"))
    
    eff_time = 40 - admin_hours
    st.info(f"💡 At {admin_hours} admin hours/week, each teacher provides {eff_time} hours of direct instruction.")

with t2:
    st.header("Teacher Ranking (Section B & D Combined)")
    ranked_df = allocator.rank_teachers(teacher_data)
    
    st.dataframe(ranked_df.style.highlight_max(subset=['Composite Score'], color='#D4EDDA'), use_container_width=True)
    
    top_tier = ranked_df.iloc[0]['Teacher Name']
    st.success(f"**Primary Recommendation:** {top_tier} is the optimal lead for High-Impact classes based on composite metrics.")
