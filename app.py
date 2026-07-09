"""app.py — FinTrack Personal Finance Dashboard — Main Entry Point."""
import streamlit as st

# You can put your password here, or better, in Streamlit secrets
# PASSWORD = "yourpassword"
PASSWORD = st.secrets.get("APP_PASSWORD", "demo123")  # fallback to demo123 if not set

def password_gate():
    if "pw_ok" not in st.session_state:
        st.session_state["pw_ok"] = False

    if not st.session_state["pw_ok"]:
        st.title("🔒 FinTrack — Password Required")
        pw = st.text_input("Enter password:", type="password")
        if st.button("Unlock"):
            if pw == PASSWORD:
                st.session_state["pw_ok"] = True
                st.experimental_rerun()
            else:
                st.error("Incorrect password. Try again.")
        st.stop()

password_gate()

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="FinTrack — Personal Finance Dashboard",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed",
)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.theme import inject_css, kpi_card, alert_card, svg_arc
from utils.formatters import (
    format_inr, format_pct,
    get_total_income, get_total_expenses, get_net_savings, get_savings_rate,
    compute_health_score, generate_smart_alerts,
)

inject_css()
DataManager.initialize()

# ─── Greeting ────────────────────────────────────────────────────────────────
data = DataManager.get()
name = data["profile"]["name"]
hour = datetime.now().hour
if hour < 12:
    greeting = "Good morning"
elif hour < 17:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

col_g, col_d = st.columns([3, 1])
with col_g:
    st.markdown(f"""
    <div style="padding:1.5rem 0 0.5rem">
        <div style="font-size:2.2rem;font-weight:800;
                    background:linear-gradient(135deg,#7c3aed,#06b6d4);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">
            {greeting}, {name} 👋
        </div>
        <div style="color:rgba(255,255,255,0.45);font-size:0.95rem;margin-top:0.25rem;">
            💎 FinTrack • {data['ui']['current_month']} • Your financial command centre
        </div>
    </div>""", unsafe_allow_html=True)

with col_d:
    st.markdown(f"""
    <div style="text-align:right;padding-top:1.8rem;color:rgba(255,255,255,0.4);font-size:0.85rem;">
        {datetime.now().strftime('%d %b %Y, %I:%M %p')}
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── Global Top Navigation ───────────────────────────────────────────────────
# This will appear on every page via st.switch_page targets
st.markdown(
    "<div class='section-header'>🔗 Quick Navigation</div>",
    unsafe_allow_html=True,
)

nav_cols = st.columns(6)
nav_items = [
    ("🏠", "Home",           "Main dashboard",                "app.py"),
    ("📊", "Dashboard",      "Charts & trends",               "pages/1_📊_Dashboard.py"),
    ("💰", "Income",         "Sources & salary",              "pages/2_💰_Income.py"),
    ("💳", "Expenses",       "Budget tracker",                "pages/3_💳_Expenses.py"),
    ("🎯", "Savings",        "Goals & SIP",                   "pages/4_🎯_Savings_Goals.py"),
    ("👤", "Profile",        "Edit defaults",                 "pages/6_👤_Profile_Defaults.py"),
]

for col, (icon, title, desc, path) in zip(nav_cols, nav_items):
    with col:
        if st.button(f"{icon} {title}", key=f"top_{title}", use_container_width=True):
            st.switch_page(path)
        st.markdown(
            f"<div style='font-size:0.7rem;color:rgba(255,255,255,0.45);margin-top:0.1rem;text-align:center;'>{desc}</div>",
            unsafe_allow_html=True,
        )

st.markdown("---")

# ─── Quick Stats KPIs ─────────────────────────────────────────────────────────
income   = get_total_income(data)
expenses = get_total_expenses(data)
savings  = get_net_savings(data)
rate     = get_savings_rate(data)

c1, c2, c3, c4 = st.columns(4)
savings_color = "#10b981" if savings >= 0 else "#ef4444"
rate_color    = "#10b981" if rate >= 20 else ("#f59e0b" if rate >= 10 else "#ef4444")

with c1:
    st.markdown(kpi_card("Monthly Income", format_inr(income), "Total active sources", "#06b6d4"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Total Expenses", format_inr(expenses), f"{format_pct(expenses/income*100 if income else 0)} of income", "#f59e0b"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("Net Savings", format_inr(savings), "Income − Expenses", savings_color), unsafe_allow_html=True)
with c4:
    sublabel = "🎯 Target: 20%" if rate >= 20 else "⚠️ Below 20% target"
    st.markdown(kpi_card("Savings Rate", format_pct(rate), sublabel, rate_color), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Health Score + Alerts ───────────────────────────────────────────────────
left, right = st.columns([1, 2])

with left:
    health = compute_health_score(data)
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;">
        <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.1em;
                    color:rgba(255,255,255,0.5);margin-bottom:0.75rem;">
            Financial Health Score
        </div>
        {svg_arc(health['score'], size=160)}
        <div style="font-size:1.1rem;font-weight:700;margin-top:0.5rem;">{health['label']}</div>
        <div style="color:rgba(255,255,255,0.4);font-size:0.8rem;margin-top:0.25rem;">
            Based on 5 key criteria
        </div>
    </div>""", unsafe_allow_html=True)

    with st.expander("📋 Score Breakdown"):
        for item in health["breakdown"]:
            icon = "✅" if item["achieved"] else "❌"
            pts  = item["points"]
            max_pts = pts if item["achieved"] else item.get("max", 0)
            st.markdown(f"{icon} **{pts}/{max_pts} pts** — {item['label']}")

with right:
    st.markdown('<div class="section-header">🔔 Smart Alerts</div>', unsafe_allow_html=True)
    alerts = generate_smart_alerts(data)
    dismissed = data["ui"].get("dismissed_alerts", [])
    visible = [a for a in alerts if a["id"] not in dismissed]

    if not visible:
        st.markdown(alert_card("emerald", "✅ **All clear!** No financial alerts this month."), unsafe_allow_html=True)
    else:
        for alert in visible[:5]:
            col_msg, col_btn = st.columns([6, 1])
            with col_msg:
                st.markdown(alert_card(alert["type"], alert["message"]), unsafe_allow_html=True)
            with col_btn:
                if st.button("✕", key=f"dismiss_{alert['id']}"):
                    DataManager.dismiss_alert(alert["id"])
                    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── Edit Profile Inline (Quick) ─────────────────────────────────────────────
with st.expander("✏️ Quick Profile Edit", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        new_name = st.text_input("Your Name", value=name, key="profile_name_home")
        if new_name != name:
            DataManager.set_key(new_name, "profile", "name")
    with c2:
        city_val = data["profile"]["city"]
        new_city = st.text_input("City", value=city_val, key="profile_city_home")
        if new_city != city_val:
            DataManager.set_key(new_city, "profile", "city")
    with c3:
        emp_types = ["Internship", "Salaried", "Freelance"]
        emp_val = data["profile"]["employment_type"]
        new_emp = st.selectbox("Employment Type", emp_types, index=emp_types.index(emp_val), key="profile_emp_home")
        if new_emp != emp_val:
            DataManager.set_key(new_emp, "profile", "employment_type")

    if st.button("🔄 Reset All Data to Defaults", type="secondary", key="reset_all_home"):
        DataManager.reset_to_defaults()
        st.rerun()
