"""utils/calculators.py — Additional financial calculation helpers."""
from utils.formatters import (
    compute_emi,
    compute_total_interest,
    compute_sip_maturity,
    compute_inhand_from_ctc,
    compute_health_score,
    generate_smart_alerts,
    get_total_income,
    get_total_expenses,
    get_net_savings,
    get_savings_rate,
)


def build_amortization_schedule(principal: float, annual_rate: float, tenure_months: int):
    """
    Returns list of dicts per month:
    {month, opening_balance, emi, principal_paid, interest_paid, closing_balance}
    """
    if tenure_months == 0:
        return []
    emi = compute_emi(principal, annual_rate, tenure_months)
    r = annual_rate / (12 * 100)
    schedule = []
    balance = principal
    for m in range(1, tenure_months + 1):
        interest_paid = balance * r
        principal_paid = emi - interest_paid
        closing = max(0, balance - principal_paid)
        schedule.append({
            "month": m,
            "opening_balance": balance,
            "emi": emi,
            "principal_paid": principal_paid,
            "interest_paid": interest_paid,
            "closing_balance": closing,
        })
        balance = closing
    return schedule


def build_amortization_yearly(principal: float, annual_rate: float, tenure_months: int):
    """Aggregated yearly principal/interest splits for stacked bar chart."""
    schedule = build_amortization_schedule(principal, annual_rate, tenure_months)
    years = {}
    for row in schedule:
        yr = (row["month"] - 1) // 12 + 1
        if yr not in years:
            years[yr] = {"year": yr, "principal": 0.0, "interest": 0.0}
        years[yr]["principal"] += row["principal_paid"]
        years[yr]["interest"] += row["interest_paid"]
    return list(years.values())


def prepayment_impact(
    principal: float, annual_rate: float, tenure_months: int, prepayment: float
):
    """Compare loan with vs without one-time prepayment."""
    without = {
        "principal": principal,
        "emi": compute_emi(principal, annual_rate, tenure_months),
        "total_interest": compute_total_interest(principal, annual_rate, tenure_months),
        "tenure": tenure_months,
    }
    new_principal = max(0, principal - prepayment)
    with_pre = {
        "principal": new_principal,
        "emi": compute_emi(new_principal, annual_rate, tenure_months),
        "total_interest": compute_total_interest(new_principal, annual_rate, tenure_months),
        "tenure": tenure_months,
    }
    with_pre["interest_saved"] = without["total_interest"] - with_pre["total_interest"]
    return without, with_pre


def build_loan_balance_series(
    principal: float, annual_rate: float, tenure_months: int, prepayment: float = 0
):
    """
    Returns monthly balance lists for without-prepay and with-prepay scenarios.
    Used by the loan balance chart.
    """
    r = annual_rate / (12 * 100)

    def balances(p, t):
        emi = compute_emi(p, annual_rate, t)
        bal = p
        result = [bal]
        for _ in range(t):
            interest = bal * r
            bal = max(0, bal - (emi - interest))
            result.append(bal)
        return result

    without = balances(principal, tenure_months)
    with_pre = balances(max(0, principal - prepayment), tenure_months)
    return without, with_pre


def sip_yearly_projection(monthly: float, annual_return_pct: float, years: int):
    """
    Returns two lists (years_list, invested_list, corpus_list) for the SIP chart.
    """
    r = annual_return_pct / (12 * 100)
    years_list, invested_list, corpus_list = [], [], []
    for yr in range(1, years + 1):
        months = yr * 12
        invested = monthly * months
        if r == 0:
            corpus = invested
        else:
            corpus = monthly * ((1 + r) ** months - 1) * (1 + r) / r
        years_list.append(yr)
        invested_list.append(invested)
        corpus_list.append(corpus)
    return years_list, invested_list, corpus_list


def dummy_cashflow_history():
    """6 months of realistic pre-loaded cash flow data."""
    return {
        "months": ["Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "May 2026", "Jun 2026"],
        "income":   [65000, 65000, 65000, 65000, 65000, 65000],
        "expenses": [52000, 49000, 47500, 46000, 43500, 43000],
        "savings":  [13000, 16000, 17500, 19000, 21500, 22000],
    }
