import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.navigation import render_top_nav
from utils.data_manager import DataManager

st.set_page_config(
    page_title="Profile — FinTrack",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_top_nav()
DataManager.initialize()

# ── Bootstrap check ───────────────────────────────────────────────────────────
DATA_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
JSON_PATH = os.path.join(DATA_DIR, "app_data.json")

if not os.path.exists(JSON_PATH):
    st.warning("⚠️ No saved data file found. Click below to create it.")
    if st.button("🚀 Create app_data.json now"):
        DataManager.save()
        st.success(f"✅ Created! File saved at: {JSON_PATH}")
        st.rerun()
else:
    st.sidebar.success("✅ app_data.json exists")

data = DataManager.get()

st.markdown("<div class='page-title'>👤 Profile & Defaults</div>", unsafe_allow_html=True)
st.markdown("---")

profile = data["profile"]
c1, c2, c3 = st.columns(3)
with c1:
    name = st.text_input("Name", value=profile["name"])
with c2:
    city = st.text_input("City", value=profile["city"])
with c3:
    emp_types = ["Internship", "Salaried", "Freelance"]
    emp_type = st.selectbox("Employment Type", emp_types, index=emp_types.index(profile["employment_type"]))

if st.button("💾 Save Profile"):
    DataManager.set_key(name, "profile", "name")
    DataManager.set_key(city, "profile", "city")
    DataManager.set_key(emp_type, "profile", "employment_type")
    st.success("Profile updated!")

if st.button("🔄 Reset All Data to Defaults"):
    DataManager.reset_to_defaults()
    st.success("All data reset — refresh the app.")
