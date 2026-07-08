"""pages/3_💳_Expenses.py — Expense tracking with budget vs actual cards."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
import pandas as pd
from utils.history import append_transactions

import streamlit as st

st.set_page_config(
    page_title="Expenses — FinTrack",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)
from utils.navigation import render_top_nav

render_top_nav()
from utils.theme import inject_css, alert_card, progress_bar
from utils.data_manager import DataManager
from utils.formatters import (
    format_inr, format_pct,
    get_total_income, get_total_expenses, get_net_savings,
    generate_smart_alerts,
)
from utils.charts import expense_donut_chart
from utils.calculators import dummy_cashflow_history

inject_css()
DataManager.initialize()
data = DataManager.get()

CHART_CFG = {"displayModeBar": False}

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1rem 0 0.25rem">
    <div class="page-title">💳 Expenses</div>
    <div style="color:rgba(255,255,255,0.4);font-size:0.9rem;">
        Track budget vs actual spending across categories
    </div>
</div>""", unsafe_allow_html=True)
st.markdown("---")

# ─── Section 1: Month Navigator ──────────────────────────────────────────────
# REPLACE with this:
from datetime import datetime
from dateutil.relativedelta import relativedelta

def generate_months(n_past: int = 6, n_future: int = 12) -> list[str]:
    """Generate month list: n_past months ago → n_future months ahead."""
    today = datetime.now().replace(day=1)
    months = []
    for i in range(-n_past, n_future + 1):
        m = today + relativedelta(months=i)
        months.append(m.strftime("%B %Y"))
    return months

MONTHS = generate_months(n_past=6, n_future=12)


col_prev, col_mid, col_next = st.columns([1, 3, 1])
with col_prev:
    if st.button("◀ Previous"):
        cur = data["ui"]["current_month"]
        if cur in MONTHS:
            idx = MONTHS.index(cur)
            if idx > 0:
                DataManager.set_key(MONTHS[idx-1], "ui", "current_month")
                st.rerun()
with col_mid:
    st.markdown(f"""
    <div style="text-align:center;font-size:1.4rem;font-weight:700;
                color:rgba(255,255,255,0.9);padding:0.25rem 0;">
        📅 {data['ui']['current_month']}
    </div>""", unsafe_allow_html=True)
with col_next:
    if st.button("Next ▶"):
        cur = data["ui"]["current_month"]
        if cur in MONTHS:
            idx = MONTHS.index(cur)
            if idx < len(MONTHS)-1:
                DataManager.set_key(MONTHS[idx+1], "ui", "current_month")
                st.rerun()

# REPLACE with:
is_current = data["ui"]["current_month"] == datetime.now().strftime("%B %Y")  # ✅
if not is_current:
    st.info(f"📖 Viewing {data['ui']['current_month']} — read-only historical view.")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 2: Expense Category Cards ───────────────────────────────────────
st.markdown('<div class="section-header">💡 Budget vs Actual by Category</div>', unsafe_allow_html=True)

income = get_total_income(data)
cats = data["expenses"]["categories"]

# 2-column grid
for row_start in range(0, len(cats), 2):
    row_cats = cats[row_start:row_start+2]
    cols = st.columns(2)
    for col, cat in zip(cols, row_cats):
        with col:
            budget = cat["budget"]
            actual = cat["actual"]
            pct    = (actual / budget * 100) if budget > 0 else 0
            inc_pct = (actual / income * 100) if income > 0 else 0

            if pct <= 75:
                bar_color = "#10b981"
                status_color = "#10b981"
                status = "✅ On track"
            elif pct <= 100:
                bar_color = "#f59e0b"
                status_color = "#f59e0b"
                status = "⚠️ Near limit"
            else:
                bar_color = "#ef4444"
                status_color = "#ef4444"
                status = "🚨 Over budget"

            st.markdown(f"""
            <div class="glass-card" style="min-height:140px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                    <div style="font-size:1rem;font-weight:700;">
                        {cat['icon']} {cat['name']}
                    </div>
                    <div style="font-size:0.75rem;color:{status_color};font-weight:600;">{status}</div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.85rem;
                            color:rgba(255,255,255,0.6);margin-bottom:0.25rem;">
                    <span>Budget: <b style="color:rgba(255,255,255,0.8);">{format_inr(budget)}</b></span>
                    <span>Actual: <b style="color:{bar_color};">{format_inr(actual)}</b></span>
                </div>
                {progress_bar(min(pct, 100), bar_color)}
                <div style="display:flex;justify-content:space-between;
                            font-size:0.75rem;color:rgba(255,255,255,0.4);margin-top:0.25rem;">
                    <span>{pct:.0f}% of budget</span>
                    <span>{inc_pct:.1f}% of income</span>
                </div>
            </div>""", unsafe_allow_html=True)

# REPLACE with this:
            if is_current:
                col_input, col_del = st.columns([4, 1])

                with col_input:
                    new_actual = st.number_input(
                        f"✏️ {cat['name']} actual (₹)",
                        value=float(actual),
                        step=100.0,
                        format="%.0f",
                        key=f"cat_actual_{cat['id']}",
                        label_visibility="collapsed",
                    )
                    if int(new_actual) != actual:
                        DataManager.update_expense_category(cat["id"], "actual", int(new_actual))
                        st.rerun()

                with col_del:
                    if st.button("🗑️", key=f"del_cat_{cat['id']}", help=f"Delete {cat['name']}"):
                        DataManager.delete_expense_category(cat["id"])
                        st.rerun()


st.markdown("<br>", unsafe_allow_html=True)


# ─── Save Transactions to Excel ──────────────────────────────────────────────
current_month = data["ui"]["current_month"]
today = datetime.now().date()

records = []
for cat in data["expenses"]["categories"]:
    if cat["actual"] > 0:
        records.append({
            "date": today,
            "month": current_month,
            "type": "expense",
            "category": cat["name"],
            "description": cat["name"],
            "amount": cat["actual"],
        })

if records and st.button("💾 Save Expense Transactions"):
    df_new = pd.DataFrame(records)
    append_transactions(df_new)
    st.success("Expense transactions saved to Excel")

st.markdown("<br>", unsafe_allow_html=True)


# ─── Add New Category ─────────────────────────────────────────────────────────
with st.expander("➕ Add New Category"):
    with st.form("add_cat_form"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: new_name   = st.text_input("Name", placeholder="e.g. Gym")
        with c2: new_icon   = st.text_input("Icon (emoji)", placeholder="e.g. 💪")
        with c3: new_budget = st.number_input("Monthly Budget (₹)", value=1000.0, step=100.0, format="%.0f")
        with c4: new_group  = st.selectbox("Group", ["Needs", "Wants", "Savings"])
        if st.form_submit_button("Add Category"):
            if new_name:
                DataManager.add_expense_category({
                    "name": new_name, "icon": new_icon or "📌",
                    "budget": int(new_budget), "actual": 0, "group": new_group
                })
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 3: 50/30/20 Analyzer ────────────────────────────────────────────
st.markdown('<div class="section-header">⚖️ 50/30/20 Budget Analyzer</div>', unsafe_allow_html=True)

needs_names  = {"Rent","Food & Groceries","Parents / Family","Transport","Phone & Internet","Health & Medical"}
wants_names  = {"Personal Care","Entertainment","Learning / Courses","Shopping / Misc"}

needs_spend  = sum(c["actual"] for c in cats if c["name"] in needs_names)
wants_spend  = sum(c["actual"] for c in cats if c["name"] in wants_names)
savings_amt  = get_net_savings(data)

needs_target  = income * 0.50
wants_target  = income * 0.30
savings_target = income * 0.20

def analyzer_card(label, emoji, actual, target, color):
    pct = actual / target * 100 if target > 0 else 0
    return f"""
    <div class="glass-card" style="text-align:center;">
        <div style="font-size:2rem;">{emoji}</div>
        <div style="font-size:1.1rem;font-weight:700;margin:0.25rem 0;">{label}</div>
        <div style="font-size:0.8rem;color:rgba(255,255,255,0.4);">Target: {format_inr(target)}</div>
        <div style="font-size:1.5rem;font-weight:800;color:{color};margin:0.5rem 0;">{format_inr(actual)}</div>
        {progress_bar(min(pct, 100), color)}
        <div style="font-size:0.8rem;color:rgba(255,255,255,0.5);">{pct:.0f}% of target</div>
    </div>"""

n_col, w_col, s_col = st.columns(3)
with n_col:
    needs_color = "#10b981" if needs_spend <= needs_target else "#ef4444"
    st.markdown(analyzer_card("NEEDS", "🏠", needs_spend, needs_target, needs_color), unsafe_allow_html=True)
with w_col:
    wants_color = "#10b981" if wants_spend <= wants_target else "#f59e0b"
    st.markdown(analyzer_card("WANTS", "✨", wants_spend, wants_target, wants_color), unsafe_allow_html=True)
with s_col:
    sav_color = "#10b981" if savings_amt >= savings_target else "#ef4444"
    st.markdown(analyzer_card("SAVINGS", "💰", max(0, savings_amt), savings_target, sav_color), unsafe_allow_html=True)

st.caption("ℹ️ 50/30/20 is a guideline. Parental support (₹20K) is classified under Needs as it's a priority commitment.")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 4: Smart Alerts ─────────────────────────────────────────────────
st.markdown('<div class="section-header">🔔 Smart Alerts</div>', unsafe_allow_html=True)

data = DataManager.get()
alerts = generate_smart_alerts(data)
dismissed = data["ui"].get("dismissed_alerts", [])
visible = [a for a in alerts if a["id"] not in dismissed]

if not visible:
    st.markdown(alert_card("emerald", "✅ **All clear!** No alerts this month."), unsafe_allow_html=True)
else:
    for alert in visible:
        col_msg, col_btn = st.columns([8, 1])
        with col_msg:
            st.markdown(alert_card(alert["type"], alert["message"]), unsafe_allow_html=True)
        with col_btn:
            if st.button("✕", key=f"exp_dismiss_{alert['id']}"):
                DataManager.dismiss_alert(alert["id"])
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 5: Expense Trend (last 6 months) ────────────────────────────────
st.markdown('<div class="section-header">📈 Expense Trend</div>', unsafe_allow_html=True)

cf = dummy_cashflow_history()
cf["expenses"][-1] = get_total_expenses(data)

import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=cf["months"], y=cf["expenses"],
    name="Total Expenses",
    line=dict(color="#f59e0b", width=3),
    marker=dict(size=8),
    fill="tozeroy",
    fillcolor="rgba(245,158,11,0.1)",
))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.7)"),
    margin=dict(l=10, r=10, t=30, b=10),
)
fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", showline=False, zeroline=False)
fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", showline=False, zeroline=False)
st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)

# Category expense summary as donut
st.markdown('<div class="section-header">🍩 Current Month Expense Mix</div>', unsafe_allow_html=True)
labels = [f"{c['icon']} {c['name']}" for c in cats]
amts   = [c["actual"] for c in cats]
fig_d  = expense_donut_chart(labels, amts)
st.plotly_chart(fig_d, use_container_width=True, config=CHART_CFG)
