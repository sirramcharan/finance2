"""utils/github_sync.py — Read/write Excel from GitHub repo."""
import io
import base64
import requests
import pandas as pd
import streamlit as st

# ── Config from Streamlit secrets ────────────────────────────────────────────
def _get_config():
    token = st.secrets["GITHUB_TOKEN"]
    repo  = st.secrets["GITHUB_REPO"]       # e.g. "charanteja/finance2"
    path  = st.secrets["EXCEL_PATH"]         # e.g. "data/finance_history.xlsx"
    return token, repo, path

def _api_url(repo: str, path: str) -> str:
    return f"https://api.github.com/repos/{repo}/contents/{path}"

def _headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

# ── Read Excel from GitHub ────────────────────────────────────────────────────
def read_excel_from_github() -> dict[str, pd.DataFrame]:
    """
    Returns dict with keys: 'transactions', 'monthly_summary'
    Each value is a DataFrame (empty if sheet missing).
    """
    token, repo, path = _get_config()
    url = _api_url(repo, path)

    resp = requests.get(url, headers=_headers(token))

    if resp.status_code == 404:
        # File doesn't exist yet — return empty frames
        return {
            "transactions":    pd.DataFrame(columns=["date","month","type","category","description","amount"]),
            "monthly_summary": pd.DataFrame(columns=["month","total_income","total_expenses","net_savings","savings_rate_pct"]),
        }

    resp.raise_for_status()
    content = base64.b64decode(resp.json()["content"])
    excel_file = io.BytesIO(content)

    sheets = {}
    for sheet in ["transactions", "monthly_summary"]:
        try:
            sheets[sheet] = pd.read_excel(excel_file, sheet_name=sheet)
        except Exception:
            sheets[sheet] = pd.DataFrame()

    return sheets


# ── Write Excel back to GitHub ────────────────────────────────────────────────
def write_excel_to_github(sheets: dict[str, pd.DataFrame], commit_msg: str = "FinTrack: update data") -> bool:
    """
    sheets = {"transactions": df1, "monthly_summary": df2}
    Returns True on success, False on failure.
    """
    token, repo, path = _get_config()
    url = _api_url(repo, path)

    # Build Excel in memory
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    buffer.seek(0)

    # Encode to base64
    encoded = base64.b64encode(buffer.read()).decode("utf-8")

    # Get current file SHA (needed for update)
    get_resp = requests.get(url, headers=_headers(token))
    sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None

    # Push to GitHub
    payload = {
        "message": commit_msg,
        "content": encoded,
    }
    if sha:
        payload["sha"] = sha  # required for updating existing file

    put_resp = requests.put(url, headers=_headers(token), json=payload)
    return put_resp.status_code in (200, 201)


# ── Convenience: append rows to transactions sheet ────────────────────────────
def append_transactions_github(new_rows: pd.DataFrame) -> bool:
    """Append new transaction rows and push back to GitHub."""
    sheets = read_excel_from_github()
    existing = sheets["transactions"]

    combined = pd.concat([existing, new_rows], ignore_index=True)
    combined.drop_duplicates(
        subset=["date", "month", "type", "category", "description"],
        keep="last",
        inplace=True,
    )
    sheets["transactions"] = combined

    return write_excel_to_github(
        sheets,
        commit_msg=f"FinTrack: add {len(new_rows)} transactions"
    )


# ── Convenience: append/update monthly summary ────────────────────────────────
def append_summary_github(summary_row: dict) -> bool:
    """Upsert a monthly summary row and push back to GitHub."""
    sheets = read_excel_from_github()
    existing = sheets["monthly_summary"]

    new_df = pd.DataFrame([summary_row])
    combined = pd.concat([existing, new_df], ignore_index=True)
    combined.drop_duplicates(subset=["month"], keep="last", inplace=True)
    combined.sort_values("month", inplace=True)

    sheets["monthly_summary"] = combined

    return write_excel_to_github(
        sheets,
        commit_msg=f"FinTrack: update summary for {summary_row['month']}"
    )
