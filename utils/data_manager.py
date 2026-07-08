"""utils/data_manager.py — Session state management for FinTrack."""
import copy
import json
import os
import streamlit as st

# ── Path to persistent JSON ──────────────────────────────────────────────────
DATA_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
JSON_PATH = os.path.join(DATA_DIR, "app_data.json")

DEFAULT_DATA = {
    # ... (keep your existing DEFAULT_DATA exactly as-is)
}


def _save_to_json(data: dict):
    """Write current app data to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _load_from_json() -> dict | None:
    """Load app data from disk. Returns None if file doesn't exist."""
    if not os.path.exists(JSON_PATH):
        return None
    try:
        with open(JSON_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        return None  # Corrupted file → fall back to defaults


class DataManager:
    KEY = "app_data"

    @classmethod
    def initialize(cls):
        """Load from JSON file first, then fall back to defaults."""
        if cls.KEY not in st.session_state:
            saved = _load_from_json()
            if saved:
                # Merge saved data with defaults (handles new keys added later)
                merged = copy.deepcopy(DEFAULT_DATA)
                cls._deep_merge(merged, saved)
                st.session_state[cls.KEY] = merged
            else:
                st.session_state[cls.KEY] = copy.deepcopy(DEFAULT_DATA)

        if "dismissed_alerts" not in st.session_state[cls.KEY]["ui"]:
            st.session_state[cls.KEY]["ui"]["dismissed_alerts"] = []

    @classmethod
    def _deep_merge(cls, base: dict, override: dict):
        """Merge override into base recursively (base is mutated)."""
        for key, val in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(val, dict):
                cls._deep_merge(base[key], val)
            else:
                base[key] = val

    @classmethod
    def save(cls):
        """Persist current session state to disk."""
        if cls.KEY in st.session_state:
            _save_to_json(st.session_state[cls.KEY])

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
        """Set a nested key AND auto-save to disk."""
        cls.initialize()
        data = st.session_state[cls.KEY]
        for k in keys[:-1]:
            data = data[k]
        data[keys[-1]] = value
        cls.save()  # ← Auto-persist on every change 💾

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
        cats = st.session_state[cls.KEY]["expenses"]["categories"]
        for cat in cats:
            if cat["id"] == cat_id:
                cat[field] = value
                break
        cls.save()  # ← Save after mutation

    @classmethod
    def update_savings_goal(cls, goal_id: int, field: str, value):
        cls.initialize()
        goals = st.session_state[cls.KEY]["savings_goals"]
        for g in goals:
            if g["id"] == goal_id:
                g[field] = value
                break
        cls.save()

    @classmethod
    def add_savings_goal(cls, goal: dict):
        cls.initialize()
        goals = st.session_state[cls.KEY]["savings_goals"]
        max_id = max((g["id"] for g in goals), default=0)
        goal["id"] = max_id + 1
        goals.append(goal)
        cls.save()

    @classmethod
    def delete_savings_goal(cls, goal_id: int):
        cls.initialize()
        goals = st.session_state[cls.KEY]["savings_goals"]
        st.session_state[cls.KEY]["savings_goals"] = [g for g in goals if g["id"] != goal_id]
        cls.save()

    @classmethod
    def add_expense_category(cls, cat: dict):
        cls.initialize()
        cats = st.session_state[cls.KEY]["expenses"]["categories"]
        max_id = max((c["id"] for c in cats), default=0)
        cat["id"] = max_id + 1
        cats.append(cat)
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
        cls.save()  # ← Save after income editor sync
