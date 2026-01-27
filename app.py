import streamlit as st
import pandas as pd
import numpy as np

# --- OPERATIONS RESEARCH ENGINE ---
class OREngine:
    """Handles the optimization logic for staff allocation."""
    
    @staticmethod
    def calculate_workload_index(gen_students, sn_students, sn_weight):
        """
        Determines the 'Effective Student Load'.
        Formula: $L = S_{gen} + (S_{sn} \times W_{sn})$
        """
        return gen_students + (sn_students * sn_weight)

    @staticmethod
    def optimize_allocation(workload, target_ratio, admin_penalty):
        """
        Calculates optimal staff count considering efficiency loss.
        Efficiency (E) = (40 - Admin Hours) / 40
        """
        efficiency_factor = (40 - admin_penalty) / 40
        raw_staff = workload / target_ratio
        # Adjusted for the time lost to administration
        optimal_staff = raw_staff / efficiency_factor
        return np.ceil(optimal_staff)

    @staticmethod
    def rank_by_capability(df):
        """
        Multi-Criteria Decision Analysis (MCDA).
        Weights: Performance (0.5), Peer Review (0.3), Seniority (0.2).
        """
        df['Capability_Index'] = (
            (df['Performance'] * 0.5) + 
            ((df['Peer_Review'] * 2) * 0.3) + # Scaling 1-5 to 1-10
            (np.log1p(df['Seniority']) * 0.2) # Log scaling for diminishing returns on seniority
        )
        return df.sort_values(by='Capability_Index', ascending=False)

# --- STREAMLIT UI ---
st.set_page_config(page_title="OR Staff Optimizer", layout="wide")

# SECTION A: STUDENT LOAD
st.header("📂 Section A: Student Load Profile")
col_a1, col_a2 = st.columns(2)
with col_a1:
    total_pop = st.number_input("Total Enrollment", value=1000)
    sn_pct = st.slider("Special Needs (SN) %", 0, 50, 15)
with col_a2:
    sn_weight = st.slider("SN Resource Multiplier", 1.0, 3.0, 2.0, help="How many 'standard' students 1 SN student equals in workload.")

# SECTION B & D: TEACHER DATA
st.header("📊 Section B & D: Teacher Capability Matrix")
# Mock dataset simulating Section B (Qualifications) and Section D (Feedback)
data = {
    "Teacher": ["Dr. Aris", "Prof. Bo", "Ms. Cy", "Mr. Di"],
    "Seniority": [15, 5, 8, 2],
    "Performance": [9.2, 8.8, 7.5, 9.5],
    "Peer_Review": [4.8, 4.0, 3.8, 4.9],
    "Satisfaction": [94, 89, 82, 91]
}
teacher_df = pd.DataFrame(data)
st.dataframe(teacher_df, use_container_width=True)

# SECTION C: EFFICIENCY PARAMETERS
st.header("⚙️ Section C: Efficiency & Constraints")
col_c1, col_c2 = st.columns(2)
with col_c1:
    ratio = st.number_input("Target Student-Teacher Ratio", value=25)
with col_c2:
    admin_hrs = st.number_input("Weekly Admin Burden (Hours)", value=8)

# --- ANALYST OPERATIONS ---
engine = OREngine()

sn_count = total_pop * (sn_pct / 100)
gen_count = total_pop - sn_count
effective_load = engine.calculate_workload_index(gen_count, sn_count, sn_weight)
optimal_staff = engine.optimize_allocation(effective_load, ratio, admin_hrs)

# --- RESULTS ---
st.divider()
res_col1, res_col2 = st.columns(2)

with res_col1:
    st.subheader("Resource Optimization Results")
    st.metric("Effective Workload", f"{effective_load:.0f} Units")
    st.metric("Optimal Staff Count", f"{int(optimal_staff)} Teachers")
    
    # Sensitivity Analysis Visualization
    st.caption("Workload Distribution (OR Analysis)")
    st.bar_chart({"General": gen_count, "Special Needs (Weighted)": sn_count * sn_weight})

with res_col2:
    st.subheader("Knowledge-Based Assignment")
    ranked_teachers = engine.rank_by_capability(teacher_df)
    st.write("Priority assignments based on Capability Index:")
    st.dataframe(ranked_teachers[['Teacher', 'Capability_Index']], use_container_width=True)

    top_choice = ranked_teachers.iloc[0]['Teacher']
    st.success(f"**Optimization Recommendation:** Deploy **{top_choice}** to the highest-complexity student cluster.")
