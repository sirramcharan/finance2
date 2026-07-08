"""pages/2_💰_Income.py — Income management with salary breakdown and FTE projection."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.github_sync import append_transactions_github


st.set_page_config(
    page_title="Income — FinTrack",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)
from utils.navigation import render_top_nav

render_top_nav()
from utils.theme import inject_css
from utils.data_manager import DataManager
from utils.formatters import (
    format_inr, format_pct,
    compute_inhand_from_ctc,
    get_total_income, get_total_expenses, get_net_savings,
)
from utils.charts import fte_comparison_bar, income_expense_gauge, wealth_path_chart

inject_css()
DataManager.initialize()
data = DataManager.get()

CHART_CFG = {"displayModeBar": False}

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1rem 0 0.25rem">
    <div class="page-title">💰 Income</div>
    <div style="color:rgba(255,255,255,0.4);font-size:0.9rem;">
        Track income sources, compute in-hand salary, and model your FTE conversion
    </div>
</div>""", unsafe_allow_html=True)
st.markdown("---")

# ─── Section 1: Income Sources ───────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Income Sources</div>', unsafe_allow_html=True)

sources_df = pd.DataFrame(data["income"]["sources"])
if "id" in sources_df.columns:
    sources_df = sources_df.drop(columns=["id"])

edited_df = st.data_editor(
    sources_df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "name":   st.column_config.TextColumn("Source Name", width="large"),
        "type":   st.column_config.SelectboxColumn(
            "Type", options=["Stipend", "Salary", "Freelance", "Passive", "Rental", "Other"]
        ),
        "amount": st.column_config.NumberColumn("Monthly Amount (₹)", format="₹%d", min_value=0),
        "status": st.column_config.SelectboxColumn(
            "Status", options=["Active", "Inactive", "Seasonal"]
        ),
    },
    hide_index=True,
    key="income_editor",
)

# Sync back
# In income.py — replace the sync block with this:
if edited_df is not None:
    records = edited_df.to_dict("records")
    for i, r in enumerate(records):
        r["id"] = i + 1

    current = data["income"]["sources"]

    # Normalize for comparison (drop id for clean diff)
    def normalize(src_list):
        return [{k: v for k, v in s.items() if k != "id"} for s in src_list]

    if normalize(records) != normalize(current):
        DataManager.update_income_sources(records)
        data = DataManager.get()


# Totals row
income_total = get_total_income(data)
st.markdown(f"""
<div class="glass-card" style="display:flex;justify-content:space-between;align-items:center;">
    <span style="font-weight:600;color:rgba(255,255,255,0.7);">Total Active Monthly Income</span>
    <span style="font-size:1.5rem;font-weight:800;color:#06b6d4;">{format_inr(income_total)}</span>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Save Transactions to Excel ──────────────────────────────────────────────
current_month = data["ui"]["current_month"]  # e.g. "2026-07"
today = datetime.now().date()

records = []
for src in data["income"]["sources"]:
    if src["status"] == "Active" and src["amount"] > 0:
        records.append({
            "date": today,
            "month": current_month,
            "type": "income",
            "category": src["type"],
            "description": src["name"],
            "amount": src["amount"],
        })

if records and st.button("💾 Save Income Transactions"):
    df_new = pd.DataFrame(records)

    with st.spinner("Saving to GitHub..."):
        ok = append_transactions_github(df_new)
    if ok:
        st.success("✅ Saved to GitHub Excel!")
    else:
        st.error("❌ Save failed — check GitHub token.")


st.markdown("<br>", unsafe_allow_html=True)


# ─── Section 2: Salaried Mode ────────────────────────────────────────────────
st.markdown('<div class="section-header">🏢 Salaried Employee — CTC Breakdown</div>', unsafe_allow_html=True)

sal_mode = st.toggle("Enable Salary Breakdown Calculator", value=data["salary_breakdown"]["enabled"], key="sal_toggle")
DataManager.set_key(sal_mode, "salary_breakdown", "enabled")

if sal_mode:
    sb = data["salary_breakdown"]
    col_in, col_out = st.columns(2)

    with col_in:
        st.markdown('<div style="color:rgba(255,255,255,0.6);margin-bottom:0.5rem;font-weight:600;">📥 CTC Inputs</div>', unsafe_allow_html=True)

        ctc = st.number_input("Annual CTC (₹)", value=float(sb["ctc_annual"]), step=50000.0, format="%.0f", key="sb_ctc")
        DataManager.set_key(int(ctc), "salary_breakdown", "ctc_annual")

        c1, c2 = st.columns(2)
        with c1:
            basic_pct = st.number_input("Basic %", value=float(sb["basic_pct"]), min_value=30.0, max_value=60.0, step=1.0, key="sb_basic")
            DataManager.set_key(basic_pct, "salary_breakdown", "basic_pct")

            hra_pct = st.number_input("HRA %", value=float(sb["hra_pct"]), min_value=0.0, max_value=50.0, step=1.0, key="sb_hra")
            DataManager.set_key(hra_pct, "salary_breakdown", "hra_pct")

            special_pct = st.number_input("Special Allowance %", value=float(sb["special_allowance_pct"]), min_value=0.0, max_value=50.0, step=1.0, key="sb_special")
            DataManager.set_key(special_pct, "salary_breakdown", "special_allowance_pct")

        with c2:
            pf_pct = st.number_input("PF %", value=float(sb["pf_pct"]), min_value=0.0, max_value=12.0, step=0.5, key="sb_pf")
            DataManager.set_key(pf_pct, "salary_breakdown", "pf_pct")

            prof_tax = st.number_input("Professional Tax (₹/month)", value=float(sb["professional_tax_monthly"]), step=100.0, format="%.0f", key="sb_pt")
            DataManager.set_key(int(prof_tax), "salary_breakdown", "professional_tax_monthly")

            tax_bracket = st.selectbox("Tax Bracket", [0, 5, 10, 15, 20, 25, 30],
                                       index=[0,5,10,15,20,25,30].index(int(sb["tax_bracket_pct"])),
                                       format_func=lambda x: f"{x}%", key="sb_tax")
            DataManager.set_key(tax_bracket, "salary_breakdown", "tax_bracket_pct")

    with col_out:
        bd = compute_inhand_from_ctc(ctc, basic_pct, hra_pct, special_pct, pf_pct, prof_tax, tax_bracket)

        breakdown_items = [
            ("Basic Salary",           bd["basic"],          "#7c3aed"),
            ("HRA",                    bd["hra"],             "#06b6d4"),
            ("Special Allowance",      bd["special_allowance"],"#f59e0b"),
            ("Gross Monthly",          bd["gross"],           "#fbbf24"),
            ("PF Deduction (Employee)",bd["pf_employee"],     "#ef4444"),
            ("PF Deduction (Employer)",bd["pf_employer"],     "#ef4444"),
            ("Professional Tax",       bd["professional_tax"],"#ef4444"),
            ("Estimated TDS",          bd["tds_monthly"],     "#ef4444"),
        ]

        st.markdown('<div style="color:rgba(255,255,255,0.6);margin-bottom:0.5rem;font-weight:600;">📤 Computed Breakdown</div>', unsafe_allow_html=True)
        for label, val, color in breakdown_items:
            sign = "−" if "Deduction" in label or label in ("Professional Tax", "Estimated TDS") else ""
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.4rem 0;
                        border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="color:rgba(255,255,255,0.65);">{label}</span>
                <span style="color:{color};font-weight:600;">{sign}{format_inr(abs(val))}/mo</span>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top:1rem;padding:1rem;border-radius:12px;
                    background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.4);">
            <div style="color:rgba(255,255,255,0.5);font-size:0.8rem;text-transform:uppercase;">Net In-Hand Monthly</div>
            <div style="font-size:2rem;font-weight:800;color:#7c3aed;margin-top:0.25rem;">
                {format_inr(bd['net_inhand_monthly'])}
            </div>
        </div>""", unsafe_allow_html=True)

        st.caption("⚠️ Based on new tax regime. Consult a CA for exact figures.")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 3: FTE Conversion Model ─────────────────────────────────────────
st.markdown('<div class="section-header">🚀 FTE Conversion Model</div>', unsafe_allow_html=True)

fte_mode = st.toggle("Model Job Conversion", value=data["income"]["fte_mode"], key="fte_toggle")
DataManager.set_key(fte_mode, "income", "fte_mode")

if fte_mode:
    col_curr, col_fte = st.columns(2)

    # Current numbers
    cur_income   = get_total_income(data)
    cur_expenses = get_total_expenses(data)
    cur_savings  = get_net_savings(data)

    with col_curr:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.08em;
                        color:rgba(255,255,255,0.4);margin-bottom:0.75rem;">Current (Internship)</div>
        """, unsafe_allow_html=True)
        st.markdown(f"**Income:** {format_inr(cur_income)}/month")
        st.markdown(f"**Expenses:** {format_inr(cur_expenses)}/month")
        st.markdown(f"**Savings:** {format_inr(cur_savings)}/month")
        st.markdown(f"**Savings Rate:** {format_pct(cur_savings/cur_income*100 if cur_income else 0)}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_fte:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.08em;color:rgba(255,255,255,0.4);margin-bottom:0.75rem;">Projected (FTE)</div>', unsafe_allow_html=True)

        fte_ctc = st.number_input("Projected CTC (₹/year)", value=float(data["income"]["fte_ctc"]),
                                   step=100000.0, format="%.0f", key="fte_ctc_input")
        DataManager.set_key(int(fte_ctc), "income", "fte_ctc")

        # Compute FTE in-hand using default breakdown
        sb = data["salary_breakdown"]
        fte_bd = compute_inhand_from_ctc(
            fte_ctc, sb["basic_pct"], sb["hra_pct"], sb["special_allowance_pct"],
            sb["pf_pct"], sb["professional_tax_monthly"], sb["tax_bracket_pct"]
        )
        fte_income   = fte_bd["net_inhand_monthly"]
        fte_expenses = cur_expenses  # assume same expenses
        fte_savings  = fte_income - fte_expenses
        fte_rate     = fte_savings / fte_income * 100 if fte_income > 0 else 0

        st.markdown(f"**Gross Monthly:** {format_inr(fte_bd['gross'])}")
        st.markdown(f"**Net In-Hand:** {format_inr(fte_income)}")
        st.markdown(f"**Projected Savings:** {format_inr(fte_savings)}/month")
        st.markdown(f"**Projected Rate:** {format_pct(fte_rate)}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Comparison chart
    intern_d = {"income": cur_income, "expenses": cur_expenses, "savings": cur_savings}
    fte_d    = {"income": fte_income, "expenses": fte_expenses, "savings": fte_savings}
    fig_cmp  = fte_comparison_bar(intern_d, fte_d)
    st.plotly_chart(fig_cmp, use_container_width=True, config=CHART_CFG)

    # 5-Year wealth projection
    st.markdown('<div class="section-header">📊 5-Year Wealth Projection</div>', unsafe_allow_html=True)

    months_i = list(range(61))
    months_f = list(range(61))
    w_intern = [cur_savings * m for m in months_i]
    w_fte    = [fte_savings * m for m in months_f]

    fig_wealth = wealth_path_chart(months_i, w_intern, months_f, w_fte)
    st.plotly_chart(fig_wealth, use_container_width=True, config=CHART_CFG)

    st.markdown(f"""
    <div class="alert-violet">
        💡 <b>FTE Impact:</b> Switching to ₹{fte_ctc/100000:.0f}L CTC adds
        <b>{format_inr(fte_savings - cur_savings)}/month</b> to your savings.
        Over 5 years that's an extra <b>{format_inr((fte_savings - cur_savings)*60)}</b>!
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 4: Income/Expense Gauge ─────────────────────────────────────────
st.markdown('<div class="section-header">⚖️ Income vs Expense Ratio</div>', unsafe_allow_html=True)

income_val   = get_total_income(data)
expenses_val = get_total_expenses(data)
exp_pct      = (expenses_val / income_val * 100) if income_val > 0 else 0

col_g, col_i = st.columns([1, 1])
with col_g:
    fig_gauge = income_expense_gauge(exp_pct)
    st.plotly_chart(fig_gauge, use_container_width=True, config=CHART_CFG)

with col_i:
    if exp_pct < 60:
        label, color, msg = "Excellent", "#10b981", "You're spending less than 60% of income — fantastic discipline!"
    elif exp_pct < 70:
        label, color, msg = "Good", "#06b6d4", "Expenses under 70% — on track for healthy savings."
    elif exp_pct < 80:
        label, color, msg = "Moderate", "#f59e0b", "Expenses between 70–80% — consider trimming wants."
    else:
        label, color, msg = "High", "#ef4444", "Expenses above 80% — review your budget immediately."

    st.markdown(f"""
    <div class="glass-card">
        <div style="font-size:1.5rem;font-weight:800;color:{color};">{label}</div>
        <div style="color:rgba(255,255,255,0.7);margin:0.5rem 0;">{msg}</div>
        <hr style="border-color:rgba(255,255,255,0.1);">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.5rem;">
            <div style="color:rgba(255,255,255,0.5);">Income</div>
            <div style="text-align:right;font-weight:600;color:#06b6d4;">{format_inr(income_val)}</div>
            <div style="color:rgba(255,255,255,0.5);">Expenses</div>
            <div style="text-align:right;font-weight:600;color:#f59e0b;">{format_inr(expenses_val)}</div>
            <div style="color:rgba(255,255,255,0.5);">Net Savings</div>
            <div style="text-align:right;font-weight:600;color:#10b981;">{format_inr(income_val - expenses_val)}</div>
            <div style="color:rgba(255,255,255,0.5);">Expense Ratio</div>
            <div style="text-align:right;font-weight:600;color:{color};">{format_pct(exp_pct)}</div>
        </div>
    </div>""", unsafe_allow_html=True)
