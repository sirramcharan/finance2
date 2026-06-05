"""pages/4_🎯_Savings_Goals.py — Goals tracker, SIP projector and net worth."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="Savings Goals — FinTrack",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.theme import inject_css, svg_ring, progress_bar
from utils.data_manager import DataManager
from utils.formatters import (
    format_inr, format_inr_short, format_pct,
    months_to_completion, compute_sip_maturity,
    get_total_income, get_total_expenses, get_net_savings,
)
from utils.calculators import sip_yearly_projection
from utils.charts import (
    savings_allocation_pie, sip_projection_area_chart, net_worth_donut,
)

inject_css()
DataManager.initialize()
data = DataManager.get()

CHART_CFG = {"displayModeBar": False}

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1rem 0 0.25rem">
    <div class="page-title">🎯 Savings Goals</div>
    <div style="color:rgba(255,255,255,0.4);font-size:0.9rem;">
        Track your financial goals, project SIP wealth and monitor net worth
    </div>
</div>""", unsafe_allow_html=True)
st.markdown("---")

# ─── Section 1: Goals Grid ────────────────────────────────────────────────────
st.markdown('<div class="section-header">🏆 My Financial Goals</div>', unsafe_allow_html=True)

goals = data["savings_goals"]
income = get_total_income(data)

for row_start in range(0, len(goals), 2):
    row_goals = goals[row_start:row_start + 2]
    cols = st.columns(2)

    for col, goal in zip(cols, row_goals):
        with col:
            progress = goal["saved"] / goal["target"] if goal["target"] > 0 else 0
            progress = min(1.0, progress)
            eta = months_to_completion(goal["target"], goal["saved"], goal["monthly_contribution"])
            pct_income = (goal["monthly_contribution"] / income * 100) if income > 0 else 0

            ring_svg = svg_ring(progress, size=110)

            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.75rem;">
                    <div>{ring_svg}</div>
                    <div style="flex:1;">
                        <div style="font-size:1.2rem;font-weight:700;">
                            {goal['icon']} {goal['name']}
                        </div>
                        <div style="font-size:0.85rem;color:rgba(255,255,255,0.5);margin-top:0.2rem;">
                            Priority #{goal['priority']}
                        </div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;font-size:0.85rem;">
                    <div style="color:rgba(255,255,255,0.5);">Saved</div>
                    <div style="text-align:right;color:#10b981;font-weight:600;">{format_inr(goal['saved'])}</div>
                    <div style="color:rgba(255,255,255,0.5);">Target</div>
                    <div style="text-align:right;color:rgba(255,255,255,0.8);font-weight:600;">{format_inr(goal['target'])}</div>
                    <div style="color:rgba(255,255,255,0.5);">Monthly</div>
                    <div style="text-align:right;color:#7c3aed;font-weight:600;">{format_inr(goal['monthly_contribution'])}</div>
                    <div style="color:rgba(255,255,255,0.5);">ETA</div>
                    <div style="text-align:right;color:#06b6d4;font-weight:600;">{eta}</div>
                </div>
                <div style="margin-top:0.6rem;font-size:0.75rem;color:rgba(255,255,255,0.35);">
                    {pct_income:.1f}% of monthly income
                </div>
            </div>""", unsafe_allow_html=True)

            with st.expander(f"✏️ Edit — {goal['name']}"):
                g_target = st.number_input(
                    "Target Amount (₹)", value=float(goal["target"]),
                    step=5000.0, format="%.0f", key=f"g_target_{goal['id']}"
                )
                g_saved = st.number_input(
                    "Amount Saved (₹)", value=float(goal["saved"]),
                    step=1000.0, format="%.0f", key=f"g_saved_{goal['id']}"
                )
                g_contrib = st.number_input(
                    "Monthly Contribution (₹)", value=float(goal["monthly_contribution"]),
                    step=500.0, format="%.0f", key=f"g_contrib_{goal['id']}"
                )
                g_name = st.text_input("Goal Name", value=goal["name"], key=f"g_name_{goal['id']}")

                col_save, col_del = st.columns(2)
                with col_save:
                    if st.button("💾 Save", key=f"g_save_{goal['id']}"):
                        DataManager.update_savings_goal(goal["id"], "target",               int(g_target))
                        DataManager.update_savings_goal(goal["id"], "saved",                int(g_saved))
                        DataManager.update_savings_goal(goal["id"], "monthly_contribution", int(g_contrib))
                        DataManager.update_savings_goal(goal["id"], "name",                 g_name)
                        st.rerun()
                with col_del:
                    if st.button("🗑️ Delete", key=f"g_del_{goal['id']}", type="secondary"):
                        DataManager.delete_savings_goal(goal["id"])
                        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── Add New Goal ─────────────────────────────────────────────────────────────
with st.expander("➕ Add New Goal"):
    with st.form("add_goal_form"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: ng_name    = st.text_input("Goal Name", placeholder="e.g. New Laptop")
        with c2: ng_icon    = st.text_input("Icon (emoji)", placeholder="💻")
        with c3: ng_target  = st.number_input("Target Amount (₹)", value=50000.0, step=5000.0, format="%.0f")
        with c4: ng_contrib = st.number_input("Monthly Contribution (₹)", value=2000.0, step=500.0, format="%.0f")

        if st.form_submit_button("🎯 Add Goal"):
            if ng_name:
                existing = data["savings_goals"]
                priority = max((g["priority"] for g in existing), default=0) + 1
                DataManager.add_savings_goal({
                    "name": ng_name, "icon": ng_icon or "🎯",
                    "target": int(ng_target), "saved": 0,
                    "monthly_contribution": int(ng_contrib), "priority": priority,
                })
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── Savings Allocation Chart ─────────────────────────────────────────────────
st.markdown('<div class="section-header">🥧 Savings Allocation</div>', unsafe_allow_html=True)
goal_names = [g["name"] for g in data["savings_goals"]]
contribs   = [g["monthly_contribution"] for g in data["savings_goals"]]
fig_pie    = savings_allocation_pie(goal_names, contribs)
st.plotly_chart(fig_pie, use_container_width=True, config=CHART_CFG)

total_monthly_goals = sum(contribs)
net_save = get_net_savings(data)
unallocated = net_save - total_monthly_goals

st.markdown(f"""
<div class="glass-card" style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
    <div style="text-align:center;">
        <div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Net Savings</div>
        <div style="font-size:1.3rem;font-weight:700;color:#06b6d4;">{format_inr(net_save)}</div>
    </div>
    <div style="text-align:center;">
        <div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Allocated to Goals</div>
        <div style="font-size:1.3rem;font-weight:700;color:#7c3aed;">{format_inr(total_monthly_goals)}</div>
    </div>
    <div style="text-align:center;">
        <div style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Unallocated</div>
        <div style="font-size:1.3rem;font-weight:700;color:{'#10b981' if unallocated >= 0 else '#ef4444'};">
            {format_inr(unallocated)}
        </div>
    </div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 2: SIP Wealth Projector ─────────────────────────────────────────
st.markdown('<div class="section-header">📈 SIP Wealth Projector</div>', unsafe_allow_html=True)

sip_goal = next((g for g in data["savings_goals"] if "SIP" in g["name"] or "Mutual" in g["name"]), None)
default_sip = sip_goal["monthly_contribution"] if sip_goal else 5000

col_in, col_out = st.columns([1, 1.5])

with col_in:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("**⚙️ SIP Parameters**")
    sip_amt    = st.number_input("Monthly SIP Amount (₹)", value=float(default_sip), step=500.0, format="%.0f", key="sip_amt")
    sip_return = st.slider("Expected Annual Return (%)", min_value=6.0, max_value=18.0, value=12.0, step=0.5, key="sip_ret")
    sip_years  = st.slider("Investment Period (years)", min_value=1, max_value=30, value=10, key="sip_yrs")
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    result = compute_sip_maturity(sip_amt, sip_return, sip_years)

    st.markdown(f"""
    <div class="glass-card">
        <div style="text-align:center;margin-bottom:1rem;">
            <div style="font-size:0.8rem;text-transform:uppercase;color:rgba(255,255,255,0.4);">
                Maturity Value after {sip_years} years
            </div>
            <div style="font-size:2.5rem;font-weight:800;color:#10b981;margin-top:0.25rem;">
                {format_inr(result['maturity_value'])}
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;text-align:center;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Total Invested</div>
                <div style="font-size:1.1rem;font-weight:700;color:#06b6d4;">{format_inr(result['total_invested'])}</div>
            </div>
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;text-align:center;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Est. Returns</div>
                <div style="font-size:1.1rem;font-weight:700;color:#7c3aed;">{format_inr(result['estimated_returns'])}</div>
            </div>
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;text-align:center;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Wealth Multiplier</div>
                <div style="font-size:1.3rem;font-weight:800;color:#fbbf24;">{result['multiplier']:.1f}×</div>
            </div>
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;text-align:center;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Return Rate</div>
                <div style="font-size:1.1rem;font-weight:700;color:#10b981;">{sip_return:.1f}% p.a.</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# SIP projection chart
yrs, invested, corpus = sip_yearly_projection(sip_amt, sip_return, sip_years)
fig_sip = sip_projection_area_chart(yrs, invested, corpus)
st.plotly_chart(fig_sip, use_container_width=True, config=CHART_CFG)

st.caption("⚠️ SIP projections assume constant returns. Actual mutual fund returns vary. Past performance is not a guarantee.")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 3: FTE Impact on Goals ──────────────────────────────────────────
st.markdown('<div class="section-header">🚀 FTE Impact on Goal Completion</div>', unsafe_allow_html=True)

show_fte = st.toggle("Show after job conversion impact", key="goals_fte_toggle")
if show_fte:
    from utils.formatters import compute_inhand_from_ctc
    sb = data["salary_breakdown"]
    fte_ctc = data["income"]["fte_ctc"]
    fte_bd  = compute_inhand_from_ctc(
        fte_ctc, sb["basic_pct"], sb["hra_pct"], sb["special_allowance_pct"],
        sb["pf_pct"], sb["professional_tax_monthly"], sb["tax_bracket_pct"]
    )
    fte_income   = fte_bd["net_inhand_monthly"]
    fte_expenses = get_total_expenses(data)
    fte_savings  = fte_income - fte_expenses

    fte_ctc_l = f"{fte_ctc/100000:.0f}L"
    st.markdown(f"""
    <div class="alert-violet">
        💼 <b>FTE Projection</b> — With <b>₹{fte_ctc_l} CTC</b>,
        your in-hand would be <b>{format_inr(fte_income)}/month</b>,
        leaving <b>{format_inr(fte_savings)}/month</b> for savings
        ({format_pct(fte_savings/fte_income*100 if fte_income > 0 else 0)} rate).
    </div>""", unsafe_allow_html=True)

    diff = fte_savings - get_net_savings(data)

    goal_rows = []
    for g in data["savings_goals"]:
        curr_eta = months_to_completion(g["target"], g["saved"], g["monthly_contribution"])
        fte_contrib = g["monthly_contribution"] + max(0, diff * (g["monthly_contribution"] / max(total_monthly_goals, 1)))
        fte_eta = months_to_completion(g["target"], g["saved"], fte_contrib)
        goal_rows.append({
            "Goal": f"{g['icon']} {g['name']}",
            "Current ETA": curr_eta,
            "FTE ETA": fte_eta,
            "Extra/month": format_inr(fte_contrib - g["monthly_contribution"]),
        })

    import pandas as pd
    st.dataframe(pd.DataFrame(goal_rows), use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 4: Net Worth Tracker ────────────────────────────────────────────
st.markdown('<div class="section-header">💎 Net Worth Tracker</div>', unsafe_allow_html=True)

col_assets, col_liabs = st.columns(2)
nw = data["net_worth"]

with col_assets:
    st.markdown("**📦 Assets**")
    import pandas as pd

    assets_list = nw["assets"]
    for i, asset in enumerate(assets_list):
        val = asset.get("amount", asset.get("grams", 0) * asset.get("rate_per_gram", 9500))
        label = asset["name"]
        if "Gold" in label:
            c1, c2 = st.columns(2)
            with c1:
                grams = st.number_input(f"Gold (grams)", value=float(asset.get("grams", 0)),
                                         step=1.0, format="%.1f", key=f"gold_g_{i}")
                assets_list[i]["grams"] = grams
            with c2:
                rate = st.number_input("Rate/gram (₹)", value=float(asset.get("rate_per_gram", 9500)),
                                        step=100.0, format="%.0f", key=f"gold_r_{i}")
                assets_list[i]["rate_per_gram"] = rate
                assets_list[i]["amount"] = grams * rate
        else:
            new_val = st.number_input(f"{label} (₹)", value=float(asset.get("amount", 0)),
                                       step=1000.0, format="%.0f", key=f"asset_{i}")
            assets_list[i]["amount"] = int(new_val)

    total_assets = sum(
        a.get("amount", a.get("grams", 0) * a.get("rate_per_gram", 9500))
        for a in assets_list
    )
    st.markdown(f"""
    <div class="alert-emerald" style="margin-top:0.5rem;">
        <b>Total Assets: {format_inr(total_assets)}</b>
    </div>""", unsafe_allow_html=True)

with col_liabs:
    st.markdown("**📉 Liabilities**")
    liabs_list = nw["liabilities"]
    for i, liab in enumerate(liabs_list):
        new_val = st.number_input(f"{liab['name']} (₹)", value=float(liab["amount"]),
                                   step=1000.0, format="%.0f", key=f"liab_{i}")
        liabs_list[i]["amount"] = int(new_val)

    total_liabs = sum(l["amount"] for l in liabs_list)
    st.markdown(f"""
    <div class="alert-red" style="margin-top:0.5rem;">
        <b>Total Liabilities: {format_inr(total_liabs)}</b>
    </div>""", unsafe_allow_html=True)

net_worth = total_assets - total_liabs
nw_color  = "#10b981" if net_worth >= 0 else "#ef4444"
nw_label  = "Net Positive 🎉" if net_worth >= 0 else "Net Negative ⚠️"

st.markdown(f"""
<div class="glass-card" style="text-align:center;margin-top:1rem;">
    <div style="font-size:0.85rem;text-transform:uppercase;color:rgba(255,255,255,0.4);">
        Net Worth = Assets − Liabilities
    </div>
    <div style="font-size:2.5rem;font-weight:800;color:{nw_color};margin:0.5rem 0;">
        {format_inr(net_worth)}
    </div>
    <div style="color:{nw_color};font-size:0.9rem;">{nw_label}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Net worth donut chart
asset_names = [a["name"] for a in assets_list]
asset_vals  = [a.get("amount", a.get("grams", 0) * a.get("rate_per_gram", 9500)) for a in assets_list]
liab_names  = [l["name"] for l in liabs_list]
liab_vals   = [l["amount"] for l in liabs_list]

fig_nw = net_worth_donut(asset_names, asset_vals, liab_names, liab_vals)
st.plotly_chart(fig_nw, use_container_width=True, config=CHART_CFG)
