"""pages/5_🏦_Loan_Manager.py — EMI calculator, prepayment simulator and rate history."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="Loan Manager — FinTrack",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)
from utils.navigation import render_top_nav

render_top_nav()
from utils.theme import inject_css
from utils.data_manager import DataManager
from utils.formatters import (
    format_inr, format_pct,
    compute_emi, compute_total_interest,
)
from utils.calculators import (
    build_amortization_yearly, prepayment_impact, build_loan_balance_series,
)
from utils.charts import (
    amortization_stacked_bar, loan_balance_chart, rate_history_line,
)

inject_css()
DataManager.initialize()
data = DataManager.get()
loan = data["loan"]

CHART_CFG  = {"displayModeBar": False}
MONTHS_MAP = {
    1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
    7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"
}

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1rem 0 0.25rem">
    <div class="page-title">🏦 Loan Manager</div>
    <div style="color:rgba(255,255,255,0.4);font-size:0.9rem;">
        EMI calculator, prepayment analysis and interest rate tracker
    </div>
</div>""", unsafe_allow_html=True)
st.markdown("---")

# ─── Section 1: Loan Overview ─────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Loan Overview</div>', unsafe_allow_html=True)

col_card, col_edit = st.columns([3, 2])

with col_card:
    emi_preview = compute_emi(loan["outstanding"], loan["rate"], loan["tenure_months"])
    tax_saving  = emi_preview * loan["tenure_months"] * (loan["tax_bracket"] / 100) / loan["tenure_months"]
    eff_rate    = loan["rate"] * (1 - loan["tax_bracket"] / 100)

    st.markdown(f"""
    <div class="glass-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
            <div>
                <div style="font-size:1.4rem;font-weight:800;">{loan['type']}</div>
                <div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">A/C: {loan['account_number']}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Status</div>
                <div style="font-size:1rem;font-weight:700;
                    color:{'#f59e0b' if loan['status']=='Moratorium' else '#10b981'};">
                    {loan['status']}
                </div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;">
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Outstanding</div>
                <div style="font-size:1.2rem;font-weight:700;color:#ef4444;">{format_inr(loan['outstanding'])}</div>
            </div>
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Interest Rate</div>
                <div style="font-size:1.2rem;font-weight:700;color:#f59e0b;">{loan['rate']:.2f}% p.a.</div>
            </div>
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Effective (80E)</div>
                <div style="font-size:1.2rem;font-weight:700;color:#10b981;">{eff_rate:.2f}% p.a.</div>
            </div>
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Tenure</div>
                <div style="font-size:1.2rem;font-weight:700;color:#7c3aed;">{loan['tenure_months']} months</div>
            </div>
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Monthly EMI</div>
                <div style="font-size:1.2rem;font-weight:700;color:#06b6d4;">{format_inr(emi_preview)}</div>
            </div>
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Tax Bracket</div>
                <div style="font-size:1.2rem;font-weight:700;color:#fbbf24;">{loan['tax_bracket']}%</div>
            </div>
        </div>
        {'<div style="margin-top:0.75rem;padding:0.6rem 1rem;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:8px;font-size:0.85rem;color:#f59e0b;">⏸️ Moratorium active — EMI not yet started</div>' if loan['status']=='Moratorium' else ''}
    </div>""", unsafe_allow_html=True)

with col_edit:
    st.markdown("**✏️ Edit Loan Details**")

    new_outstanding = st.number_input(
        "Outstanding Principal (₹)", value=float(loan["outstanding"]),
        step=1000.0, format="%.0f", key="loan_outstanding"
    )
    DataManager.set_key(int(new_outstanding), "loan", "outstanding")

    new_rate = st.number_input(
        "Interest Rate (% p.a.)", value=float(loan["rate"]),
        step=0.05, format="%.3f", key="loan_rate"
    )
    DataManager.set_key(new_rate, "loan", "rate")

    new_tenure = st.slider(
        "Tenure (months)", min_value=12, max_value=120,
        value=int(loan["tenure_months"]), step=6, key="loan_tenure"
    )
    DataManager.set_key(new_tenure, "loan", "tenure_months")

    new_tax = st.selectbox(
        "Tax Bracket", [0, 5, 10, 15, 20, 25, 30],
        index=[0, 5, 10, 15, 20, 25, 30].index(int(loan["tax_bracket"])),
        format_func=lambda x: f"{x}%", key="loan_tax"
    )
    DataManager.set_key(new_tax, "loan", "tax_bracket")

    status_opts = ["Moratorium", "Active EMI"]
    new_status = st.radio("Loan Status", status_opts,
                           index=0 if loan["status"] == "Moratorium" else 1,
                           horizontal=True, key="loan_status")
    DataManager.set_key(new_status.replace(" EMI", ""), "loan", "status")

    if new_status == "Moratorium":
        c1, c2 = st.columns(2)
        with c1:
            months_list = list(MONTHS_MAP.values())
            default_m_idx = 6
            emi_m = st.selectbox("EMI Start Month",
                                  months_list,
                                  index=default_m_idx,
                                  key="emi_start_month")
            DataManager.set_key(list(MONTHS_MAP.keys())[months_list.index(emi_m)], "loan", "emi_start_month")
        with c2:
            emi_y = st.number_input("EMI Start Year", value=2026, step=1, format="%d", key="emi_start_year")
            DataManager.set_key(int(emi_y), "loan", "emi_start_year")

        emi_month = DataManager.get_key("loan", "emi_start_month")
        emi_year  = DataManager.get_key("loan", "emi_start_year")
        if emi_month:
            preview_emi = compute_emi(
                DataManager.get_key("loan", "outstanding"),
                DataManager.get_key("loan", "rate"),
                DataManager.get_key("loan", "tenure_months")
            )
            st.markdown(f"""
            <div class="alert-cyan">
                📅 EMI starts <b>{MONTHS_MAP.get(emi_month,'')} {emi_year}</b><br>
                Projected monthly EMI: <b>{format_inr(preview_emi)}</b>
            </div>""", unsafe_allow_html=True)

# Reload loan after edits
data = DataManager.get()
loan = data["loan"]

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 2: EMI Calculator ────────────────────────────────────────────────
st.markdown('<div class="section-header">🧮 EMI Calculator</div>', unsafe_allow_html=True)

col_calc_in, col_calc_out = st.columns(2)

with col_calc_in:
    calc_principal = st.number_input(
        "Principal (₹)", value=float(loan["outstanding"]),
        step=1000.0, format="%.0f", key="calc_p"
    )
    calc_rate = st.number_input(
        "Annual Interest Rate (%)", value=float(loan["rate"]),
        step=0.05, format="%.3f", key="calc_r"
    )
    calc_tenure = st.slider(
        "Tenure (months)", min_value=12, max_value=120,
        value=int(loan["tenure_months"]), step=6, key="calc_t"
    )
    calc_tax = st.selectbox(
        "Tax Bracket for 80E", [0, 5, 10, 15, 20, 25, 30],
        index=[0, 5, 10, 15, 20, 25, 30].index(int(loan["tax_bracket"])),
        format_func=lambda x: f"{x}%", key="calc_tax"
    )

with col_calc_out:
    emi           = compute_emi(calc_principal, calc_rate, calc_tenure)
    total_int     = compute_total_interest(calc_principal, calc_rate, calc_tenure)
    total_payable = calc_principal + total_int
    eff_r         = calc_rate * (1 - calc_tax / 100)
    annual_tax_sav = total_int / calc_tenure * 12 * calc_tax / 100

    st.markdown(f"""
    <div class="glass-card">
        <div style="text-align:center;margin-bottom:1rem;">
            <div style="font-size:0.8rem;text-transform:uppercase;color:rgba(255,255,255,0.4);">Monthly EMI</div>
            <div style="font-size:2.5rem;font-weight:800;color:#7c3aed;">{format_inr(emi)}</div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;">
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Total Interest</div>
                <div style="font-size:1.1rem;font-weight:700;color:#ef4444;">{format_inr(total_int)}</div>
            </div>
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Total Payable</div>
                <div style="font-size:1.1rem;font-weight:700;color:#f59e0b;">{format_inr(total_payable)}</div>
            </div>
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Effective Rate (80E)</div>
                <div style="font-size:1.1rem;font-weight:700;color:#10b981;">{eff_r:.2f}%</div>
            </div>
            <div style="padding:0.75rem;background:rgba(255,255,255,0.04);border-radius:10px;">
                <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);">Annual Tax Saving</div>
                <div style="font-size:1.1rem;font-weight:700;color:#fbbf24;">{format_inr(annual_tax_sav)}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# Amortization chart
yearly = build_amortization_yearly(calc_principal, calc_rate, calc_tenure)
fig_amortz = amortization_stacked_bar(yearly)
st.plotly_chart(fig_amortz, use_container_width=True, config=CHART_CFG)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 3: Prepayment Simulator ─────────────────────────────────────────
st.markdown('<div class="section-header">💸 Prepayment Simulator</div>', unsafe_allow_html=True)

prepay_amt = st.number_input(
    "One-time Prepayment Amount (₹)",
    value=float(loan.get("prepayment_amount", 100000)),
    step=10000.0, format="%.0f", key="prepay_amt"
)
DataManager.set_key(int(prepay_amt), "loan", "prepayment_amount")

principal = loan["outstanding"]
rate      = loan["rate"]
tenure    = loan["tenure_months"]

without, with_pre = prepayment_impact(principal, rate, tenure, prepay_amt)

col_wo, col_wi = st.columns(2)

with col_wo:
    st.markdown(f"""
    <div class="glass-card" style="border-color:rgba(245,158,11,0.3);">
        <div style="font-size:1rem;font-weight:700;color:#f59e0b;margin-bottom:0.75rem;">
            ❌ Without Prepayment
        </div>
        <div style="display:flex;flex-direction:column;gap:0.5rem;">
            <div style="display:flex;justify-content:space-between;">
                <span style="color:rgba(255,255,255,0.5);">Principal</span>
                <span style="font-weight:600;">{format_inr(without['principal'])}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:rgba(255,255,255,0.5);">Monthly EMI</span>
                <span style="font-weight:600;">{format_inr(without['emi'])}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:rgba(255,255,255,0.5);">Tenure</span>
                <span style="font-weight:600;">{without['tenure']} months</span>
            </div>
            <div style="display:flex;justify-content:space-between;border-top:1px solid rgba(255,255,255,0.1);padding-top:0.5rem;">
                <span style="color:rgba(255,255,255,0.5);">Total Interest</span>
                <span style="font-weight:700;color:#ef4444;">{format_inr(without['total_interest'])}</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

with col_wi:
    months_saved = without["tenure"] - with_pre["tenure"]
    st.markdown(f"""
    <div class="glass-card" style="border-color:rgba(16,185,129,0.4);">
        <div style="font-size:1rem;font-weight:700;color:#10b981;margin-bottom:0.75rem;">
            ✅ With {format_inr(prepay_amt)} Prepayment
        </div>
        <div style="display:flex;flex-direction:column;gap:0.5rem;">
            <div style="display:flex;justify-content:space-between;">
                <span style="color:rgba(255,255,255,0.5);">New Principal</span>
                <span style="font-weight:600;">{format_inr(with_pre['principal'])}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:rgba(255,255,255,0.5);">Monthly EMI</span>
                <span style="font-weight:600;">{format_inr(with_pre['emi'])}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:rgba(255,255,255,0.5);">Tenure</span>
                <span style="font-weight:600;">{with_pre['tenure']} months</span>
            </div>
            <div style="display:flex;justify-content:space-between;border-top:1px solid rgba(255,255,255,0.1);padding-top:0.5rem;">
                <span style="color:rgba(255,255,255,0.5);">Total Interest</span>
                <span style="font-weight:700;color:#10b981;">{format_inr(with_pre['total_interest'])}</span>
            </div>
        </div>
        <div style="margin-top:1rem;padding:0.6rem;border-radius:8px;
                    background:rgba(16,185,129,0.1);text-align:center;">
            <div style="color:#10b981;font-weight:700;font-size:0.95rem;">
                💰 You save {format_inr(with_pre['interest_saved'])} in interest!
            </div>
            <div style="color:#7c3aed;font-weight:600;font-size:0.85rem;margin-top:0.2rem;">
                🗓️ Loan closes {months_saved} months earlier
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# Loan balance chart
bal_wo, bal_wi = build_loan_balance_series(principal, rate, tenure, prepay_amt)
fig_bal = loan_balance_chart(list(range(len(bal_wo))), bal_wo, bal_wi)
st.plotly_chart(fig_bal, use_container_width=True, config=CHART_CFG)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 4: Interest Rate History ────────────────────────────────────────
st.markdown('<div class="section-header">📉 Interest Rate History</div>', unsafe_allow_html=True)

rate_history = loan["rate_history"]

# Timeline display
for entry in rate_history:
    change = entry["to_rate"] - entry["from_rate"]
    direction = "▼" if change < 0 else "▲"
    color     = "#10b981" if change < 0 else "#ef4444"
    st.markdown(f"""
    <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
            <div>
                <div style="font-weight:600;">{entry['date']}</div>
                <div style="color:rgba(255,255,255,0.5);font-size:0.85rem;">
                    {entry['from_rate']:.3f}% → <b style="color:white;">{entry['to_rate']:.3f}%</b>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:1.2rem;font-weight:700;color:{color};">
                    {direction} {abs(change):.3f}%
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# Rate history line chart
if rate_history:
    # Build dates + rates for step line
    dates = []
    rates = []
    for entry in rate_history:
        dates.append(entry["date"])
        rates.append(entry["to_rate"])
    fig_rate = rate_history_line(dates, rates)
    st.plotly_chart(fig_rate, use_container_width=True, config=CHART_CFG)

# Add rate change form
with st.expander("➕ Add Rate Change"):
    with st.form("add_rate_form"):
        c1, c2, c3 = st.columns(3)
        with c1: new_date      = st.text_input("Date (DD/MM/YYYY)", placeholder="01/07/2026")
        with c2: new_from_rate = st.number_input("From Rate (%)", value=float(loan["rate"]), step=0.05, format="%.3f")
        with c3: new_to_rate   = st.number_input("To Rate (%)", value=float(loan["rate"]), step=0.05, format="%.3f")
        if st.form_submit_button("Add Rate Change"):
            if new_date:
                DataManager.add_rate_history({
                    "date": new_date, "from_rate": new_from_rate, "to_rate": new_to_rate
                })
                DataManager.set_key(new_to_rate, "loan", "rate")
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 5: Gold Loan Comparison ─────────────────────────────────────────
st.markdown('<div class="section-header">🥇 Gold Loan vs Education Loan Comparison</div>', unsafe_allow_html=True)

gold_rate   = st.number_input(
    "Gold Loan Rate (%)", value=float(loan["gold_loan_rate"]),
    step=0.25, format="%.2f", key="gold_rate_input"
)
DataManager.set_key(gold_rate, "loan", "gold_loan_rate")

edu_rate    = loan["rate"]
tax_bracket = loan["tax_bracket"]
eff_edu     = edu_rate * (1 - tax_bracket / 100)
tenure_cmp  = 60

emi_edu  = compute_emi(principal, edu_rate, tenure_cmp)
emi_gold = compute_emi(principal, gold_rate, tenure_cmp)
int_edu  = compute_total_interest(principal, edu_rate, tenure_cmp)
int_gold = compute_total_interest(principal, gold_rate, tenure_cmp)

monthly_saving = emi_gold - emi_edu

st.markdown(f"""
<div class="glass-card">
    <table class="compare-table">
        <thead>
            <tr>
                <th>Metric</th>
                <th>🎓 Education Loan</th>
                <th>🥇 Gold Loan</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Interest Rate</td>
                <td><b>{edu_rate:.2f}%</b></td>
                <td>{gold_rate:.2f}%</td>
            </tr>
            <tr>
                <td>Section 80E Deduction</td>
                <td style="color:#10b981;font-weight:700;">✅ Yes</td>
                <td style="color:#ef4444;">❌ No</td>
            </tr>
            <tr>
                <td>Effective Rate ({tax_bracket}% bracket)</td>
                <td style="color:#10b981;font-weight:700;"><b>~{eff_edu:.2f}%</b></td>
                <td style="color:#ef4444;">{gold_rate:.2f}%</td>
            </tr>
            <tr>
                <td>Monthly EMI (60 months)</td>
                <td style="color:#10b981;font-weight:700;"><b>{format_inr(emi_edu)}</b></td>
                <td>{format_inr(emi_gold)}</td>
            </tr>
            <tr>
                <td>Total Interest</td>
                <td style="color:#10b981;font-weight:700;"><b>{format_inr(int_edu)}</b></td>
                <td>{format_inr(int_gold)}</td>
            </tr>
            <tr>
                <td>Collateral Risk</td>
                <td style="color:#10b981;">✅ None</td>
                <td style="color:#ef4444;">⚠️ Gold seizure risk</td>
            </tr>
            <tr>
                <td>Tenure Flexibility</td>
                <td style="color:#10b981;">✅ High (up to 15 yrs)</td>
                <td style="color:#ef4444;">❌ Low (1–3 yrs)</td>
            </tr>
            <tr>
                <td><b>Verdict</b></td>
                <td style="color:#10b981;font-weight:700;font-size:1rem;">✅ RECOMMENDED</td>
                <td style="color:#ef4444;font-weight:700;">❌ NOT ADVISED</td>
            </tr>
        </tbody>
    </table>
</div>""", unsafe_allow_html=True)

recommendation = f"""
💡 <b>Keep your education loan.</b> After Section 80E tax deduction at {tax_bracket}% bracket,
your effective interest rate is <b>~{eff_edu:.2f}%</b> vs gold loan's <b>{gold_rate:.2f}%</b>.
{"You save <b>" + format_inr(abs(monthly_saving)) + "/month</b>. " if eff_edu < gold_rate else ""}
Protect your family's gold — it's a valuable safety net.
The education loan also builds your credit history and has no asset at risk.
"""

alert_type = "emerald" if eff_edu < gold_rate else "amber"
st.markdown(f'<div class="alert-{alert_type}" style="margin-top:1rem;">{recommendation}</div>',
            unsafe_allow_html=True)
