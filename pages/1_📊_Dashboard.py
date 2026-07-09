"""pages/1_📊_Dashboard.py — Main dashboard with charts and KPIs."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.github_sync import append_summary_github


import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard — FinTrack",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)
#from utils.navigation import render_top_nav

# REPLACE with:
from utils.navigation import check_password, render_top_nav
check_password()   # ← blocks page if not unlocked
render_top_nav()

from utils.theme import inject_css, svg_arc
from utils.data_manager import DataManager
from utils.formatters import (
    format_inr, format_pct,
    get_total_income, get_total_expenses, get_net_savings, get_savings_rate,
    compute_health_score,
)
from utils.calculators import dummy_cashflow_history
from utils.charts import (
    cash_flow_bar_chart, expense_donut_chart, savings_allocation_pie,
    monthly_snapshot_line,
)

inject_css()
DataManager.initialize()
data = DataManager.get()

CHART_CFG = {"displayModeBar": False}

# ─── Page Header ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1rem 0 0.25rem">
    <div class="page-title">📊 Dashboard</div>
    <div style="color:rgba(255,255,255,0.4);font-size:0.9rem;">
        Your financial overview for the current month
    </div>
</div>""", unsafe_allow_html=True)
st.markdown("---")

# ─── Section 1: KPI Cards ────────────────────────────────────────────────────
income   = get_total_income(data)
expenses = get_total_expenses(data)
savings  = get_net_savings(data)
rate     = get_savings_rate(data)

# ─── Save Snapshot to Excel ──────────────────────────────────────────────────
current_month = data["ui"]["current_month"]

# REPLACE WITH:
if st.button("💾 Save Monthly Snapshot"):
    summary_row = {
        "month": current_month,
        "total_income": income,
        "total_expenses": expenses,
        "net_savings": savings,
        "savings_rate_pct": rate,
    }
    with st.spinner("Saving to GitHub..."):
        ok = append_summary_github(summary_row)
    if ok:
        st.success("✅ Monthly summary saved to GitHub Excel!")
    else:
        st.error("❌ Save failed — check GitHub token in Streamlit secrets.")



st.markdown("<br>", unsafe_allow_html=True)



c1, c2, c3, c4 = st.columns(4)

with c1:
    delta_inc = None
    st.metric("💰 Total Income", format_inr(income), help="Sum of all active income sources")
    with st.expander("✏️ Edit Income", expanded=False):
        sources = data["income"]["sources"]
        for i, src in enumerate(sources):
            if src["status"] == "Active":
                new_amt = st.number_input(
                    f"{src['name']}", value=float(src["amount"]),
                    step=1000.0, format="%.0f", key=f"inc_amt_{src['id']}"
                )
                if new_amt != src["amount"]:
                    sources[i]["amount"] = int(new_amt)

with c2:
    st.metric("💳 Total Expenses", format_inr(expenses),
              delta=f"{format_pct(expenses/income*100 if income else 0)} of income",
              delta_color="inverse")
    with st.expander("✏️ Quick Adjust", expanded=False):
        st.caption("Edit expenses in the Expenses page for full breakdown.")

with c3:
    savings_delta = f"{'▲' if savings >= 0 else '▼'} from ₹0 baseline"
    st.metric("💹 Net Savings", format_inr(savings),
              delta=savings_delta,
              delta_color="normal" if savings >= 0 else "inverse")

with c4:
    benchmark = "🎯 At target!" if rate >= 20 else "⚠️ Below 20% target"
    st.metric("📈 Savings Rate", format_pct(rate), delta=benchmark,
              delta_color="normal" if rate >= 20 else "off")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 2: Cash Flow Chart ───────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Cash Flow — Last 6 Months</div>', unsafe_allow_html=True)

cf = dummy_cashflow_history()
# Replace last month with actual
cf["income"][-1]   = income
cf["expenses"][-1] = expenses
cf["savings"][-1]  = savings

fig_cf = cash_flow_bar_chart(cf["months"], cf["income"], cf["expenses"], cf["savings"])
st.plotly_chart(fig_cf, use_container_width=True, config=CHART_CFG)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 3: Donut + Pie ───────────────────────────────────────────────────
col_left, col_right = st.columns([6, 4])

with col_left:
    st.markdown('<div class="section-header">🍩 Expense Breakdown</div>', unsafe_allow_html=True)
    cats   = data["expenses"]["categories"]
    labels = [f"{c['icon']} {c['name']}" for c in cats]
    amts   = [c["actual"] for c in cats]
    fig_donut = expense_donut_chart(labels, amts)
    st.plotly_chart(fig_donut, use_container_width=True, config=CHART_CFG)

with col_right:
    st.markdown('<div class="section-header">🎯 Savings Allocation</div>', unsafe_allow_html=True)
    goals       = data["savings_goals"]
    goal_names  = [g["name"] for g in goals]
    contribs    = [g["monthly_contribution"] for g in goals]
    fig_pie     = savings_allocation_pie(goal_names, contribs)
    st.plotly_chart(fig_pie, use_container_width=True, config=CHART_CFG)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 4: Monthly Snapshot Table ───────────────────────────────────────
st.markdown('<div class="section-header">📅 Monthly Snapshot</div>', unsafe_allow_html=True)

# Build 6-month table
cf_data = dummy_cashflow_history()
cf_data["income"][-1]   = income
cf_data["expenses"][-1] = expenses
cf_data["savings"][-1]  = savings

rows = []
for i, month in enumerate(cf_data["months"]):
    inc  = cf_data["income"][i]
    exp  = cf_data["expenses"][i]
    sav  = cf_data["savings"][i]
    r    = sav / inc * 100 if inc > 0 else 0
    status = "🟢 On Track" if r >= 20 else ("🟡 Moderate" if r >= 10 else "🔴 Low")
    rows.append({
        "Month": month,
        "Income": format_inr(inc),
        "Expenses": format_inr(exp),
        "Net Savings": format_inr(sav),
        "Savings Rate": format_pct(r),
        "Status": status,
    })

df = pd.DataFrame(rows)
st.dataframe(
    df,
    use_container_width=True,
    column_config={
        "Month":        st.column_config.TextColumn("Month"),
        "Income":       st.column_config.TextColumn("Income"),
        "Expenses":     st.column_config.TextColumn("Expenses"),
        "Net Savings":  st.column_config.TextColumn("Net Savings"),
        "Savings Rate": st.column_config.TextColumn("Savings Rate"),
        "Status":       st.column_config.TextColumn("Status"),
    },
    hide_index=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 5: Savings Rate Trend ───────────────────────────────────────────
st.markdown('<div class="section-header">📈 Savings Rate Trend</div>', unsafe_allow_html=True)

saving_rates = []
for i in range(len(cf_data["months"])):
    inc = cf_data["income"][i]
    sav = cf_data["savings"][i]
    saving_rates.append(round(sav / inc * 100, 1) if inc > 0 else 0)

fig_line = monthly_snapshot_line(cf_data["months"], saving_rates)
st.plotly_chart(fig_line, use_container_width=True, config=CHART_CFG)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 6: Health Score Detail ──────────────────────────────────────────
st.markdown('<div class="section-header">🏥 Financial Health Score</div>', unsafe_allow_html=True)

health = compute_health_score(data)

col_arc, col_detail = st.columns([1, 3])

with col_arc:
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;padding:2rem 1rem;">
        {svg_arc(health['score'], size=180)}
        <div style="font-size:1.3rem;font-weight:800;margin-top:0.75rem;">{health['label']}</div>
    </div>""", unsafe_allow_html=True)

with col_detail:
    with st.expander("📋 Score Breakdown — Click to expand", expanded=True):
        total_pts = 0
        for item in health["breakdown"]:
            achieved = item["achieved"]
            pts      = item["points"]
            max_pts  = pts if achieved else item.get("max", 0)
            icon     = "✅" if achieved else "❌"
            color    = "#10b981" if achieved else "#ef4444"
            total_pts += pts
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.75rem;
                        padding:0.5rem;border-radius:8px;margin-bottom:0.4rem;
                        background:rgba(255,255,255,0.03);">
                <span style="font-size:1.2rem;">{icon}</span>
                <span style="flex:1;color:rgba(255,255,255,0.8);">{item['label']}</span>
                <span style="font-weight:700;color:{color};">{pts}/{max_pts} pts</span>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top:1rem;padding:0.75rem;border-radius:10px;
                    background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);
                    text-align:center;font-size:1.1rem;font-weight:700;">
            Total: {health['score']}/100 — {health['label']}
        </div>""", unsafe_allow_html=True)

    st.caption("💡 Tip: Aim for a score of 80+ by maintaining a 20% savings rate and 6-month emergency fund.")
