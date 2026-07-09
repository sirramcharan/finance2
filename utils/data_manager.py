"""utils/data_manager.py — Session state management for FinTrack."""
import copy
import json
import os
import streamlit as st
from datetime import datetime
# ── Persistence paths ─────────────────────────────────────────────────────────
DATA_DIR  = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)
JSON_PATH = os.path.join(DATA_DIR, "app_data.json")

# ── Disk helpers ──────────────────────────────────────────────────────────────
def _save_to_json(data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=2, default=str)

def _load_from_json() -> dict | None:
    if not os.path.exists(JSON_PATH):
        return None
    try:
        with open(JSON_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        return None

# ── Default Data ──────────────────────────────────────────────────────────────
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
            {"id": 2, "name": "Freelance / Side Income",               "type": "Freelance","amount": 0,     "status": "Inactive"},
            {"id": 3, "name": "Interest / Passive Income",             "type": "Passive",  "amount": 0,     "status": "Inactive"},
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
            {"id": 1,  "name": "Rent",              "icon": "🏠",  "budget": 15000, "actual": 15000, "group": "Needs"},
            {"id": 2,  "name": "Food & Groceries",  "icon": "🍽️",  "budget": 7000,  "actual": 7000,  "group": "Needs"},
            {"id": 3,  "name": "Parents / Family",  "icon": "👨‍👩‍👧", "budget": 20000, "actual": 20000, "group": "Needs"},
            {"id": 4,  "name": "Transport",         "icon": "🚌",  "budget": 3000,  "actual": 0,     "group": "Needs"},
            {"id": 5,  "name": "Phone & Internet",  "icon": "📱",  "budget": 500,   "actual": 500,   "group": "Needs"},
            {"id": 6,  "name": "Health & Medical",  "icon": "🏥",  "budget": 1000,  "actual": 0,     "group": "Needs"},
            {"id": 7,  "name": "Personal Care",     "icon": "💆",  "budget": 1000,  "actual": 500,   "group": "Wants"},
            {"id": 8,  "name": "Entertainment",     "icon": "🎉",  "budget": 1500,  "actual": 0,     "group": "Wants"},
            {"id": 9,  "name": "Learning / Courses","icon": "📚",  "budget": 1000,  "actual": 0,     "group": "Wants"},
            {"id": 10, "name": "Shopping / Misc",   "icon": "🛍️",  "budget": 2000,  "actual": 0,     "group": "Wants"},
        ],
        "month_history": {},
    },
    "savings_goals": [
        {"id": 1, "name": "Emergency Fund",      "icon": "🛡️", "target": 150000, "saved": 0, "monthly_contribution": 15000, "priority": 1},
        {"id": 2, "name": "SIP / Mutual Fund",   "icon": "📈", "target": 60000,  "saved": 0, "monthly_contribution": 5000,  "priority": 2},
        {"id": 3, "name": "Loan Prepayment Fund","icon": "💰", "target": 100000, "saved": 0, "monthly_contribution": 3000,  "priority": 3},
        {"id": 4, "name": "Travel Fund",         "icon": "✈️", "target": 30000,  "saved": 0, "monthly_contribution": 0,     "priority": 4},
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
            {"date": "15/12/2025", "from_rate": 10.150, "to_rate":  9.900},
        ],
        "prepayment_amount": 100000,
        "gold_loan_rate": 9.50,
    },
    "net_worth": {
        "assets": [
            {"name": "Cash / Savings",     "amount": 0},
            {"name": "SIP / Mutual Funds", "amount": 0},
            {"name": "Gold (grams)",       "grams": 0, "rate_per_gram": 9500},
            {"name": "Other Assets",       "amount": 0},
        ],
        "liabilities": [
            {"name": "Education Loan",  "amount": 551985},
            {"name": "Other Loans",     "amount": 0},
            {"name": "Credit Card Due", "amount": 0},
        ],
    },
    # Then change DEFAULT_DATA "ui" section to:
    "ui": {
        "dismissed_alerts": [],
        "current_month": datetime.now().strftime("%B %Y"),  # ← always today's month
    },
}


# ── DataManager ───────────────────────────────────────────────────────────────
class DataManager:
    """Manages all app data via session_state + JSON persistence."""

    KEY = "app_data"

    # REPLACE WITH:
    @classmethod
    def initialize(cls):
        from datetime import datetime
        if cls.KEY not in st.session_state:
            # Try loading from GitHub Excel first
            try:
                from utils.state_sync import load_app_state_from_github
                saved = load_app_state_from_github()
            except Exception:
                saved = None
    
            if saved:
                merged = copy.deepcopy(DEFAULT_DATA)
                cls._deep_merge(merged, saved)
                st.session_state[cls.KEY] = merged
            else:
                st.session_state[cls.KEY] = copy.deepcopy(DEFAULT_DATA)
    
        ui = st.session_state[cls.KEY].setdefault("ui", {})
        ui.setdefault("dismissed_alerts", [])
        ui.setdefault("current_month", datetime.now().strftime("%B %Y"))
    

    @classmethod
    def _deep_merge(cls, base: dict, override: dict):
        for key, val in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(val, dict):
                cls._deep_merge(base[key], val)
            else:
                base[key] = val

    # REPLACE WITH:
    @classmethod
    def save(cls):
        """Save to GitHub Excel (primary) + local JSON (backup)."""
        if cls.KEY not in st.session_state:
            return
        try:
            from utils.state_sync import save_app_state_to_github
            save_app_state_to_github(st.session_state[cls.KEY])
        except Exception as e:
            st.warning(f"⚠️ GitHub save skipped: {e}")
        # Also save local JSON as backup
        try:
            _save_to_json(st.session_state[cls.KEY])
        except Exception:
            pass


    @classmethod
    def get(cls) -> dict:
        cls.initialize()
        return st.session_state[cls.KEY]

    @classmethod
    def get_key(cls, *keys):
        data = cls.get()
        for k in keys:
            data = data[k]
        return data

    @classmethod
    def set_key(cls, value, *keys):
        cls.initialize()
        data = st.session_state[cls.KEY]
        for k in keys[:-1]:
            data = data[k]
        data[keys[-1]] = value
        cls.save()

    @classmethod
    def reset_to_defaults(cls):
        st.session_state[cls.KEY] = copy.deepcopy(DEFAULT_DATA)
        cls.save()

    @classmethod
    def dismiss_alert(cls, alert_id: str):
        cls.initialize()
        dismissed = st.session_state[cls.KEY]["ui"]["dismissed_alerts"]
        if alert_id not in dismissed:
            dismissed.append(alert_id)
        cls.save()

    @classmethod
    def is_alert_dismissed(cls, alert_id: str) -> bool:
        cls.initialize()
        return alert_id in st.session_state[cls.KEY]["ui"]["dismissed_alerts"]

    @classmethod
    def update_expense_category(cls, cat_id: int, field: str, value):
        cls.initialize()
        for cat in st.session_state[cls.KEY]["expenses"]["categories"]:
            if cat["id"] == cat_id:
                cat[field] = value
                break
        cls.save()

    @classmethod
    def update_savings_goal(cls, goal_id: int, field: str, value):
        cls.initialize()
        for g in st.session_state[cls.KEY]["savings_goals"]:
            if g["id"] == goal_id:
                g[field] = value
                break
        cls.save()

    @classmethod
    def add_savings_goal(cls, goal: dict):
        cls.initialize()
        goals = st.session_state[cls.KEY]["savings_goals"]
        goal["id"] = max((g["id"] for g in goals), default=0) + 1
        goals.append(goal)
        cls.save()

    @classmethod
    def delete_savings_goal(cls, goal_id: int):
        cls.initialize()
        goals = st.session_state[cls.KEY]["savings_goals"]
        st.session_state[cls.KEY]["savings_goals"] = [
            g for g in goals if g["id"] != goal_id
        ]
        cls.save()

    @classmethod
    def add_expense_category(cls, cat: dict):
        cls.initialize()
        cats = st.session_state[cls.KEY]["expenses"]["categories"]
        cat["id"] = max((c["id"] for c in cats), default=0) + 1
        cats.append(cat)
        cls.save()
    @classmethod
    def delete_expense_category(cls, cat_id: int):
        """Delete an expense category by id."""
        cls.initialize()
        cats = st.session_state[cls.KEY]["expenses"]["categories"]
        st.session_state[cls.KEY]["expenses"]["categories"] = [
            c for c in cats if c["id"] != cat_id
        ]
        cls.save()

    @classmethod
    def add_rate_history(cls, entry: dict):
        cls.initialize()
        st.session_state[cls.KEY]["loan"]["rate_history"].append(entry)
        cls.save()

    @classmethod
    def update_income_sources(cls, sources: list):
        cls.initialize()
        st.session_state[cls.KEY]["income"]["sources"] = sources
        cls.save()
