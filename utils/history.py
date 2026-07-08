import os
import pandas as pd

HIST_PATH = os.path.join("data", "finance_history.xlsx")

def load_history():
    trans = pd.read_excel(HIST_PATH, sheet_name="transactions")
    monthly = pd.read_excel(HIST_PATH, sheet_name="monthly_summary")
    return trans, monthly

def append_transactions(new_rows_df: pd.DataFrame):
    trans, monthly = load_history()
    trans = pd.concat([trans, new_rows_df], ignore_index=True)

    # Overwrite the entire file with updated sheets
    with pd.ExcelWriter(HIST_PATH, engine="openpyxl", mode="w") as writer:
        trans.to_excel(writer, sheet_name="transactions", index=False)
        monthly.to_excel(writer, sheet_name="monthly_summary", index=False)

def append_month_summary(summary_row: dict):
    trans, monthly = load_history()
    monthly = pd.concat([monthly, pd.DataFrame([summary_row])], ignore_index=True)

    # Overwrite the entire file with updated sheets
    with pd.ExcelWriter(HIST_PATH, engine="openpyxl", mode="w") as writer:
        trans.to_excel(writer, sheet_name="transactions", index=False)
        monthly.to_excel(writer, sheet_name="monthly_summary", index=False)
