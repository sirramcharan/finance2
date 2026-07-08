import os
import pandas as pd

HIST_PATH = os.path.join("data", "finance_history.xlsx")

TRANSACTION_COLUMNS = [
    "date", "month", "type", "category", "description", "amount",
]

MONTHLY_COLUMNS = [
    "month", "total_income", "total_expenses", "net_savings", "savings_rate_pct",
]

def _init_empty_excel():
    transactions = pd.DataFrame(columns=TRANSACTION_COLUMNS)
    monthly = pd.DataFrame(columns=MONTHLY_COLUMNS)
    with pd.ExcelWriter(HIST_PATH) as writer:
        transactions.to_excel(writer, sheet_name="transactions", index=False)
        monthly.to_excel(writer, sheet_name="monthly_summary", index=False)

def load_history():
    if not os.path.exists(HIST_PATH):
        _init_empty_excel()
    trans = pd.read_excel(HIST_PATH, sheet_name="transactions")
    monthly = pd.read_excel(HIST_PATH, sheet_name="monthly_summary")
    return trans, monthly

def append_transactions(new_rows_df: pd.DataFrame):
    trans, monthly = load_history()
    trans = pd.concat([trans, new_rows_df], ignore_index=True)
    with pd.ExcelWriter(HIST_PATH, engine="openpyxl", mode="w") as writer:
        trans.to_excel(writer, sheet_name="transactions", index=False)
        monthly.to_excel(writer, sheet_name="monthly_summary", index=False)

def append_month_summary(summary_row: dict):
    trans, monthly = load_history()
    monthly = pd.concat([monthly, pd.DataFrame([summary_row])], ignore_index=True)
    with pd.ExcelWriter(HIST_PATH, engine="openpyxl", mode="w") as writer:
        trans.to_excel(writer, sheet_name="transactions", index=False)
        monthly.to_excel(writer, sheet_name="monthly_summary", index=False)
