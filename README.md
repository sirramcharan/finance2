# FinTrack 💎 — Personal Finance Dashboard

A sleek glassmorphism-themed personal finance tracker built with Streamlit,
designed for Indian urban professionals.

---

## Features

| Page | Description |
|------|-------------|
| 🏠 **Home** | Greeting, KPI cards, health score, smart alerts |
| 📊 **Dashboard** | Cash flow charts, expense donut, savings trend |
| 💰 **Income** | Source editor, CTC breakdown, FTE model |
| 💳 **Expenses** | Budget vs actual, 50/30/20 analyzer |
| 🎯 **Savings Goals** | Goals tracker, SIP projector, net worth |
| 🏦 **Loan Manager** | EMI calculator, prepayment simulator, rate history |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## Project Structure

```
fintrack/
├── app.py                      ← Homepage + entry point
├── pages/
│   ├── 1_📊_Dashboard.py       ← KPIs, charts, health score
│   ├── 2_💰_Income.py          ← Income sources + salary breakdown
│   ├── 3_💳_Expenses.py        ← Budget tracker + 50/30/20
│   ├── 4_🎯_Savings_Goals.py   ← Goals + SIP projector + net worth
│   └── 5_🏦_Loan_Manager.py    ← EMI + prepayment + rate history
├── utils/
│   ├── data_manager.py         ← Session state management
│   ├── formatters.py           ← Indian ₹ formatting + calculations
│   ├── calculators.py          ← Amortization, SIP, prepayment
│   ├── charts.py               ← All Plotly chart builders
│   └── theme.py                ← CSS injection + HTML components
├── assets/
│   └── style.css               ← Reference CSS (injected via theme.py)
├── data/
│   └── default_data.json       ← Default data reference
├── .streamlit/
│   └── config.toml             ← Dark theme config
├── requirements.txt
└── README.md
```

---

## Default Data

Pre-loaded with realistic Indian urban professional defaults:

- **Income:** ₹65,000/month stipend (NetApp internship)
- **Loan:** Education loan ₹5,51,985 @ 9.90% p.a. (Moratorium)
- **Expenses:** Bangalore living costs (Rent ₹15K, Parents ₹20K, etc.)
- **Goals:** Emergency Fund, SIP, Loan Prepayment, Travel Fund

> All data lives in Streamlit session state. Refresh the browser to reset.

---

## Key Calculations

| Feature | Formula |
|---------|---------|
| **EMI** | `P × r × (1+r)ⁿ / ((1+r)ⁿ − 1)` |
| **SIP Maturity** | `M × ((1+r)ⁿ − 1) × (1+r) / r` |
| **Effective Loan Rate** | `Rate × (1 − Tax Bracket %)` |
| **Health Score** | 5 criteria, max 100 pts |
| **Indian Formatting** | `₹5,51,985` / `₹5.52L` / `₹1.2Cr` |

---

## Deploy to Streamlit Cloud

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → set **Main file path** to `app.py`
4. Click **Deploy**

The `.streamlit/config.toml` theme is automatically picked up.

---

## Design System

**Glassmorphism Dark Theme:**
- Background: Deep purple-to-navy radial gradient
- Cards: `rgba(255,255,255,0.05)` with `backdrop-filter: blur(20px)`
- Accent palette: Violet `#7c3aed` · Cyan `#06b6d4` · Emerald `#10b981` · Amber `#f59e0b`
- All Plotly charts: Transparent backgrounds, consistent color sequence

---

## Notes

- ⚠️ Tax and in-hand calculations use the **new tax regime** (simplified).
  Consult a CA for exact figures.
- 📊 Historical cash flow data (Jan–May 2026) is pre-populated for demo purposes.
- 🔒 No external API calls — fully offline after `pip install`.
- 🔄 Use the **Reset All Data** button on the home page to restore defaults.
