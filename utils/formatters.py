"""utils/formatters.py — Formatting, calculation and analysis utilities."""
import math


# ─── Number Formatting ──────────────────────────────────────────────────────

def format_inr(n: float) -> str:
    """Format number in full Indian number system: ₹5,51,985"""
    if n is None:
        return "₹0"
    negative = n < 0
    n_int = int(abs(round(n)))
    s = str(n_int)
    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        rest = s[:-3]
        parts = []
        while len(rest) > 2:
            parts.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.append(rest)
        parts.reverse()
        formatted = ",".join(parts) + "," + last3
    prefix = "−" if negative else ""
    return prefix + "₹" + formatted


def format_inr_short(n: float) -> str:
    """₹5.5L, ₹1.2Cr for large numbers in charts/labels."""
    if n is None:
        return "₹0"
    negative = n < 0
    n = abs(n)
    prefix = "−" if negative else ""
    if n >= 10_000_000:
        return f"{prefix}₹{n/10_000_000:.2f}Cr"
    elif n >= 100_000:
        return f"{prefix}₹{n/100_000:.2f}L"
    elif n >= 1_000:
        return f"{prefix}₹{n/1_000:.1f}K"
    else:
        return f"{prefix}₹{int(n)}"


def format_pct(value: float, decimals: int = 1) -> str:
    """Format as percentage string: 35.4%"""
    return f"{value:.{decimals}f}%"


# ─── Time Utilities ──────────────────────────────────────────────────────────

def months_to_completion(target: float, saved: float, monthly: float) -> str:
    """Return human-readable completion time."""
    if saved >= target:
        return "Goal reached! 🎉"
    if monthly <= 0:
        return "No contribution set"
    remaining = target - saved
    months = math.ceil(remaining / monthly)
    if months < 12:
        return f"{months} month{'s' if months != 1 else ''}"
    years = months // 12
    rem = months % 12
    y_str = f"{years} year{'s' if years != 1 else ''}"
    return y_str if rem == 0 else f"{y_str} {rem} month{'s' if rem != 1 else ''}"


# ─── Financial Calculators ───────────────────────────────────────────────────

def compute_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """EMI = P × r × (1+r)^n / ((1+r)^n − 1)"""
    if annual_rate == 0 or tenure_months == 0:
        return principal / max(tenure_months, 1)
    r = annual_rate / (12 * 100)
    n = tenure_months
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def compute_total_interest(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Total interest paid over loan tenure."""
    emi = compute_emi(principal, annual_rate, tenure_months)
    return emi * tenure_months - principal


def compute_sip_maturity(monthly: float, annual_return_pct: float, years: int) -> dict:
    """Return SIP maturity breakdown."""
    months = years * 12
    r = annual_return_pct / (12 * 100)
    if r == 0:
        maturity_value = monthly * months
    else:
        maturity_value = monthly * ((1 + r) ** months - 1) * (1 + r) / r
    total_invested = monthly * months
    estimated_returns = maturity_value - total_invested
    multiplier = maturity_value / total_invested if total_invested > 0 else 0
    return {
        "total_invested": total_invested,
        "estimated_returns": estimated_returns,
        "maturity_value": maturity_value,
        "multiplier": multiplier,
    }


def compute_inhand_from_ctc(
    ctc_annual: float,
    basic_pct: float,
    hra_pct: float,
    special_pct: float,
    pf_pct: float,
    prof_tax: float,
    tax_bracket_pct: float,
) -> dict:
    """Full CTC-to-in-hand breakdown (new tax regime)."""
    basic_m = ctc_annual * basic_pct / 100 / 12
    hra_m = ctc_annual * hra_pct / 100 / 12
    special_m = ctc_annual * special_pct / 100 / 12
    gross_m = basic_m + hra_m + special_m
    pf_emp_m = basic_m * pf_pct / 100
    pf_er_m = basic_m * pf_pct / 100
    # Simplified new regime TDS
    taxable_annual = ctc_annual - 50_000 - pf_emp_m * 12
    tds_m = max(0, taxable_annual * tax_bracket_pct / 100) / 12
    net_m = gross_m - pf_emp_m - prof_tax - tds_m
    return {
        "basic": basic_m,
        "hra": hra_m,
        "special_allowance": special_m,
        "gross": gross_m,
        "pf_employee": pf_emp_m,
        "pf_employer": pf_er_m,
        "professional_tax": prof_tax,
        "tds_monthly": tds_m,
        "net_inhand_monthly": net_m,
    }


# ─── Business Logic ───────────────────────────────────────────────────────────

def get_total_income(app_data: dict) -> float:
    return sum(
        s["amount"] for s in app_data["income"]["sources"] if s["status"] == "Active"
    )


def get_total_expenses(app_data: dict) -> float:
    return sum(c["actual"] for c in app_data["expenses"]["categories"])


def get_net_savings(app_data: dict) -> float:
    return get_total_income(app_data) - get_total_expenses(app_data)


def get_savings_rate(app_data: dict) -> float:
    income = get_total_income(app_data)
    if income == 0:
        return 0.0
    return get_net_savings(app_data) / income * 100


def compute_health_score(app_data: dict) -> dict:
    """Score 0-100 across 5 criteria."""
    score = 0
    breakdown = []

    income = get_total_income(app_data) or 65_000
    expenses = get_total_expenses(app_data)
    savings_rate = (income - expenses) / income * 100 if income else 0

    # 1. Savings rate ≥ 20% → 25 pts
    if savings_rate >= 20:
        score += 25
        breakdown.append({"label": f"Savings rate {savings_rate:.1f}% ≥ 20%", "points": 25, "achieved": True})
    else:
        breakdown.append({"label": f"Savings rate {savings_rate:.1f}% (need 20%)", "points": 0, "achieved": False, "max": 25})

    # 2. Emergency fund ≥ 3 months → 25 pts
    emergency = next((g for g in app_data["savings_goals"] if "Emergency" in g["name"]), None)
    em_months = (emergency["saved"] / expenses) if (emergency and expenses > 0) else 0
    if em_months >= 3:
        score += 25
        breakdown.append({"label": f"Emergency fund {em_months:.1f} months ≥ 3", "points": 25, "achieved": True})
    else:
        breakdown.append({"label": f"Emergency fund {em_months:.1f} months (need 3)", "points": 0, "achieved": False, "max": 25})

    # 3. Loan not overdue → 20 pts
    if app_data["loan"]["status"] in ("Moratorium", "Active"):
        score += 20
        breakdown.append({"label": "Loan in good standing", "points": 20, "achieved": True})
    else:
        breakdown.append({"label": "Loan status issue", "points": 0, "achieved": False, "max": 20})

    # 4. Expenses < 70% income → 20 pts
    exp_pct = expenses / income * 100 if income else 100
    if exp_pct < 70:
        score += 20
        breakdown.append({"label": f"Expenses {exp_pct:.1f}% of income (< 70%)", "points": 20, "achieved": True})
    else:
        breakdown.append({"label": f"Expenses {exp_pct:.1f}% of income (need < 70%)", "points": 0, "achieved": False, "max": 20})

    # 5. Active SIP → 10 pts
    sip = next((g for g in app_data["savings_goals"] if "SIP" in g["name"] or "Mutual" in g["name"]), None)
    has_sip = sip and sip.get("monthly_contribution", 0) > 0
    if has_sip:
        score += 10
        breakdown.append({"label": "Active SIP investment", "points": 10, "achieved": True})
    else:
        breakdown.append({"label": "No active SIP (start investing!)", "points": 0, "achieved": False, "max": 10})

    if score >= 80:
        label = "Excellent 🌟"
    elif score >= 60:
        label = "Good 👍"
    elif score >= 40:
        label = "Fair ⚠️"
    else:
        label = "Needs Work 🔧"

    return {"score": score, "breakdown": breakdown, "label": label}


def generate_smart_alerts(app_data: dict) -> list:
    """Generate contextual financial alerts."""
    alerts = []
    income = get_total_income(app_data) or 65_000
    expenses = get_total_expenses(app_data)
    savings_rate = (income - expenses) / income * 100 if income else 0

    # 1. Over-budget categories
    for cat in app_data["expenses"]["categories"]:
        if cat["actual"] > cat["budget"] > 0:
            over = cat["actual"] - cat["budget"]
            alerts.append({
                "type": "amber",
                "message": f"⚠️ **{cat['icon']} {cat['name']}** over budget by **{format_inr(over)}** "
                           f"(Budget: {format_inr(cat['budget'])}, Actual: {format_inr(cat['actual'])})",
                "id": f"over_budget_{cat['id']}",
            })

    # 2. Low savings rate
    if savings_rate < 20:
        alerts.append({
            "type": "red",
            "message": f"🚨 **Savings rate is {savings_rate:.1f}%** — below the recommended 20%. Consider reducing discretionary spending.",
            "id": "low_savings_rate",
        })

    # 3. Zero transport
    transport = next((c for c in app_data["expenses"]["categories"] if "Transport" in c["name"]), None)
    if transport and transport["actual"] == 0:
        alerts.append({
            "type": "cyan",
            "message": "ℹ️ **Transport** expense is ₹0 this month — did you forget to log commute costs?",
            "id": "transport_zero",
        })

    # 4. High parental support
    parents = next((c for c in app_data["expenses"]["categories"] if "Parent" in c["name"] or "Family" in c["name"]), None)
    if parents and income > 0:
        p_pct = parents["actual"] / income * 100
        if p_pct >= 30:
            alerts.append({
                "type": "cyan",
                "message": f"ℹ️ **Family support** is {p_pct:.1f}% of income ({format_inr(parents['actual'])}). This is your priority — noted and respected.",
                "id": "high_parents_pct",
            })

    # 5. Great expense discipline
    if income > 0 and (expenses / income * 100) < 65:
        alerts.append({
            "type": "emerald",
            "message": f"✅ **Great discipline!** Your expenses are only {expenses/income*100:.1f}% of income. You're on track!",
            "id": "low_expense_praise",
        })

    # 6. No SIP
    sip = next((g for g in app_data["savings_goals"] if "SIP" in g["name"] or "Mutual" in g["name"]), None)
    has_sip = sip and sip.get("monthly_contribution", 0) > 0
    if not has_sip:
        alerts.append({
            "type": "violet",
            "message": "💡 **Start a SIP** — even ₹1,000/month in an index fund can grow 3–5× over 10 years with compounding.",
            "id": "no_sip",
        })

    # 7. Critical emergency fund
    emergency = next((g for g in app_data["savings_goals"] if "Emergency" in g["name"]), None)
    if emergency and expenses > 0:
        em_months = emergency["saved"] / expenses
        if em_months < 1:
            alerts.append({
                "type": "red",
                "message": f"🚨 **Emergency fund critically low** — only {em_months:.1f} months of expenses covered. Target: 6 months.",
                "id": "low_emergency_fund",
            })

    # 8. No EMI start date
    if app_data["loan"]["status"] == "Moratorium" and app_data["loan"]["emi_start_month"] is None:
        alerts.append({
            "type": "amber",
            "message": "📅 **EMI start date not set** for your education loan. Plan your timeline in the Loan Manager.",
            "id": "no_emi_date",
        })

    return alerts
