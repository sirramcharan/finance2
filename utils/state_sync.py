"""utils/state_sync.py — Save and load full app state via GitHub Excel."""
import io
import copy
import base64
import requests
import pandas as pd
import json
import streamlit as st

def _get_config():
    token = st.secrets["GITHUB_TOKEN"]
    repo  = st.secrets["GITHUB_REPO"]
    path  = st.secrets["EXCEL_PATH"]
    return token, repo, path

def _api_url(repo, path):
    return f"https://api.github.com/repos/{repo}/contents/{path}"

def _headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

def _get_sha(token, repo, path):
    """Get current file SHA from GitHub (needed to update file)."""
    resp = requests.get(_api_url(repo, path), headers=_headers(token))
    if resp.status_code == 200:
        return resp.json().get("sha")
    return None

def _read_raw_excel(token, repo, path) -> io.BytesIO | None:
    """Download raw Excel bytes from GitHub."""
    resp = requests.get(_api_url(repo, path), headers=_headers(token))
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    content = base64.b64decode(resp.json()["content"])
    return io.BytesIO(content)


# ── Load app state from Excel ─────────────────────────────────────────────────
def load_app_state_from_github() -> dict | None:
    """
    Read app_state sheet from Excel.
    Returns the saved state dict, or None if not found.
    """
    try:
        token, repo, path = _get_config()
        raw = _read_raw_excel(token, repo, path)
        if raw is None:
            return None

        try:
            df = pd.read_excel(raw, sheet_name="app_state")
        except Exception:
            return None  # sheet doesn't exist yet

        if df.empty or "json_data" not in df.columns:
            return None

        json_str = df["json_data"].iloc[0]
        return json.loads(json_str)

    except Exception as e:
        st.warning(f"⚠️ Could not load saved state: {e}")
        return None


# ── Save app state to Excel ───────────────────────────────────────────────────
def save_app_state_to_github(app_data: dict) -> bool:
    """
    Write full app state as JSON into app_state sheet.
    Preserves existing transactions + monthly_summary sheets.
    """
    try:
        token, repo, path = _get_config()
        raw = _read_raw_excel(token, repo, path)

        # Read existing sheets to preserve them
        existing_sheets = {}
        if raw is not None:
            for sheet in ["transactions", "monthly_summary"]:
                try:
                    raw.seek(0)
                    existing_sheets[sheet] = pd.read_excel(raw, sheet_name=sheet)
                except Exception:
                    existing_sheets[sheet] = pd.DataFrame()
        else:
            existing_sheets["transactions"]    = pd.DataFrame(
                columns=["date","month","type","category","description","amount"]
            )
            existing_sheets["monthly_summary"] = pd.DataFrame(
                columns=["month","total_income","total_expenses","net_savings","savings_rate_pct"]
            )

        # Serialize app_data as JSON into a single-row DataFrame
        json_str = json.dumps(app_data, default=str)
        state_df = pd.DataFrame([{"json_data": json_str}])

        # Write all sheets back
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            existing_sheets["transactions"].to_excel(
                writer, sheet_name="transactions", index=False
            )
            existing_sheets["monthly_summary"].to_excel(
                writer, sheet_name="monthly_summary", index=False
            )
            state_df.to_excel(writer, sheet_name="app_state", index=False)
        buffer.seek(0)

        # Push to GitHub
        encoded = base64.b64encode(buffer.read()).decode("utf-8")
        sha     = _get_sha(token, repo, path)

        payload = {
            "message": "FinTrack: save app state",
            "content": encoded,
        }
        if sha:
            payload["sha"] = sha

        resp = requests.put(
            _api_url(repo, path),
            headers=_headers(token),
            json=payload,
        )
        return resp.status_code in (200, 201)

    except Exception as e:
        st.error(f"❌ Save failed: {e}")
        return False
