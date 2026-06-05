"""utils/data_manager.py — Session state management for FinTrack."""
import copy
import streamlit as st

DEFAULT_DATA = {
    "profile": {
        "name": "Charan",
        "city": "Bangalore",
        "employment_type": "Internship",
        "currency": "INR",
    },
    "income": {
        "sources": [
            {"id": 1, "name": "NetApp AI & Digital Experience Intern", "type": "Stipend",  "amount": 65000, "status": "Active"},
            {"id": 2, "name": "Freelance / Side Income",              "type": "Freelance", "amount": 0,     "status": "Inactive"},
            {"id": 3, "name": "Interest / Passive Income",            "type": "Passive",   "amount": 0,     "status": "Inactive"},
        ],
        "fte_mode": False,
        "fte_ctc": 1_600_000,
        "fte_start_month": 7,
    },
    "salary_breakdown": {
        "enabled": False,
        "ctc_annual": 1_600_000,
        "basic_pct": 40,
        "hra_pct": 20,
        "special_allowance_pct": 30,
        "pf_pct": 12,
        "professional_tax_monthly": 200,
        "tax_bracket_pct": 20,
    },
    "expenses": {
        "categories": [
            {"id": 1,  "name": "Rent",             "icon": "🏠", "budget": 15000, "actual": 15000, "group": "Needs"},
            {"id": 2,  "name": "Food & Groceries", "icon": "🍽️", "budget": 7000,  "actual": 7000,  "group": "Needs"},
            {"id": 3,  "name": "Parents / Family", "icon": "👨‍👩‍👧", "budget": 20000, "actual": 20000, "group": "Needs"},
            {"id": 4,  "name": "Transport",        "icon": "🚌", "budget": 3000,  "actual": 0,     "group": "Needs"},
            {"id": 5,  "name": "Phone & Internet", "icon": "📱", "budget": 500,   "actual": 500,   "group": "Needs"},
            {"id": 6,  "name": "Health & Medical", "icon": "🏥", "budget": 1000,  "actual": 0,     "group": "Needs"},
            {"id": 7,  "name": "Personal Care",    "icon": "💆", "budget": 1000,  "actual": 500,   "group": "Wants"},
            {"id": 8,  "name": "Entertainment",    "icon": "🎉", "budget": 1500,  "actual": 0,     "group": "Wants"},
            {"id": 9,  "name": "Learning / Courses","icon": "📚", "budget": 1000,  "actual": 0,     "group": "Wants"},
            {"id": 10, "name": "Shopping / Misc",  "icon": "🛍️", "budget": 2000,  "actual": 0,     "group": "Wants"},
        ],
        "month_history": {},
    },
    "savings_goals": [
        {"id": 1, "name": "Emergency Fund",     "icon": "🛡️", "target": 150000, "saved": 0,  "monthly_contribution": 15000, "priority": 1},
        {"id": 2, "name": "SIP / Mutual Fund",  "icon": "📈", "target": 60000,  "saved": 0,  "monthly_contribution": 5000,  "priority": 2},
        {"id": 3, "name": "Loan Prepayment Fund","icon": "💰", "target": 100000, "saved": 0,  "monthly_contribution": 3000,  "priority": 3},
        {"id": 4, "name": "Travel Fund",        "icon": "✈️", "target": 30000,  "saved": 0,  "monthly_contribution": 0,     "priority": 4},
    ],
    "loan": {
        "account_number": "XXXXXXX5062",
        "outstanding": 551985,
        "rate": 9.90,
        "type": "Education Loan",
        "status": "Moratorium",
        "emi_start_month": None,
        "emi_start_year": None,
        "tenure_months": 60,
        "tax_bracket": 20,
        "rate_history": [
            {"date": "10/06/2025", "from_rate": 12.650, "to_rate": 10.650},
            {"date": "15/06/2025", "from_rate": 10.650, "to_rate": 10.150},
            {"date": "15/12/2025", "from_rate": 10.150, "to_rate": 9.900},
        ],
        "prepayment_amount": 100000,
        "gold_loan_rate": 9.50,
    },
    "net_worth": {
        "assets": [
            {"name": "Cash / Savings",    "amount": 0},
            {"name": "SIP / Mutual Funds", "amount": 0},
            {"name": "Gold (grams)",      "grams": 0, "rate_per_gram": 9500},
            {"name": "Other Assets",      "amount": 0},
        ],
        "liabilities": [
            {"name": "Education Loan",  "amount": 551985},
            {"name": "Other Loans",     "amount": 0},
            {"name": "Credit Card Due", "amount": 0},
        ],
    },
    "ui": {
        "dismissed_alerts": [],
        "current_month": "June 2026",
    },
}


class DataManager:
    """Manages all app data through Streamlit session_state."""

    KEY = "app_data"

    @classmethod
    def initialize(cls):
        """Initialize session_state with defaults on first load."""
        if cls.KEY not in st.session_state:
            st.session_state[cls.KEY] = copy.deepcopy(DEFAULT_DATA)
        # Ensure dismissed_alerts list exists
        if "dismissed_alerts" not in st.session_state[cls.KEY]["ui"]:
            st.session_state[cls.KEY]["ui"]["dismissed_alerts"] = []

    @classmethod
    def get(cls) -> dict:
        """Get the full app_data dict."""
        cls.initialize()
        return st.session_state[cls.KEY]

    @classmethod
    def get_key(cls, *keys):
        """Drill into nested keys: get_key('loan', 'outstanding')"""
        data = cls.get()
        for k in keys:
            data = data[k]
        return data

    @classmethod
    def set_key(cls, value, *keys):
        """Set a nested key value."""
        cls.initialize()
        data = st.session_state[cls.KEY]
        for k in keys[:-1]:
            data = data[k]
        data[keys[-1]] = value

    @classmethod
    def reset_to_defaults(cls):
        """Reset all data to defaults."""
        st.session_state[cls.KEY] = copy.deepcopy(DEFAULT_DATA)

    @classmethod
    def dismiss_alert(cls, alert_id: str):
        """Mark an alert as dismissed."""
        cls.initialize()
        dismissed = st.session_state[cls.KEY]["ui"]["dismissed_alerts"]
        if alert_id not in dismissed:
            dismissed.append(alert_id)

    @classmethod
    def is_alert_dismissed(cls, alert_id: str) -> bool:
        cls.initialize()
        return alert_id in st.session_state[cls.KEY]["ui"]["dismissed_alerts"]

    @classmethod
    def update_expense_category(cls, cat_id: int, field: str, value):
        """Update a specific expense category field."""
        cls.initialize()
        cats = st.session_state[cls.KEY]["expenses"]["categories"]
        for cat in cats:
            if cat["id"] == cat_id:
                cat[field] = value
                break

    @classmethod
    def update_savings_goal(cls, goal_id: int, field: str, value):
        """Update a specific savings goal field."""
        cls.initialize()
        goals = st.session_state[cls.KEY]["savings_goals"]
        for g in goals:
            if g["id"] == goal_id:
                g[field] = value
                break

    @classmethod
    def add_savings_goal(cls, goal: dict):
        """Add a new savings goal."""
        cls.initialize()
        goals = st.session_state[cls.KEY]["savings_goals"]
        max_id = max((g["id"] for g in goals), default=0)
        goal["id"] = max_id + 1
        goals.append(goal)

    @classmethod
    def delete_savings_goal(cls, goal_id: int):
        """Delete a savings goal by id."""
        cls.initialize()
        goals = st.session_state[cls.KEY]["savings_goals"]
        st.session_state[cls.KEY]["savings_goals"] = [g for g in goals if g["id"] != goal_id]

    @classmethod
    def add_expense_category(cls, cat: dict):
        """Add a new expense category."""
        cls.initialize()
        cats = st.session_state[cls.KEY]["expenses"]["categories"]
        max_id = max((c["id"] for c in cats), default=0)
        cat["id"] = max_id + 1
        cats.append(cat)

    @classmethod
    def add_rate_history(cls, entry: dict):
        """Add a rate history entry to the loan."""
        cls.initialize()
        st.session_state[cls.KEY]["loan"]["rate_history"].append(entry)

    @classmethod
    def update_income_sources(cls, sources: list):
        """Replace all income sources (from data_editor)."""
        cls.initialize()
        st.session_state[cls.KEY]["income"]["sources"] = sources
