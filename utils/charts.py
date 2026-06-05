"""utils/charts.py — All Plotly chart builder functions for FinTrack."""
import plotly.graph_objects as go
import plotly.express as px

COLORS = ["#7c3aed", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#fbbf24"]
VIOLET  = "#7c3aed"
CYAN    = "#06b6d4"
EMERALD = "#10b981"
AMBER   = "#f59e0b"
RED     = "#ef4444"
GOLD    = "#fbbf24"


def _base_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="rgba(255,255,255,0.8)")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.7)", family="Inter, sans-serif"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(
            bgcolor="rgba(255,255,255,0.05)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
        ),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", showline=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", showline=False, zeroline=False)
    return fig


def cash_flow_bar_chart(months, income_list, expense_list, savings_list) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Income",   x=months, y=income_list,   marker_color=CYAN,    opacity=0.85))
    fig.add_trace(go.Bar(name="Expenses", x=months, y=expense_list,  marker_color=AMBER,   opacity=0.85))
    fig.add_trace(go.Bar(name="Savings",  x=months, y=savings_list,  marker_color=VIOLET,  opacity=0.85))
    fig.update_layout(barmode="group")
    _base_layout(fig, "Cash Flow — Last 6 Months")
    return fig


def expense_donut_chart(categories, amounts) -> go.Figure:
    # Only show non-zero categories
    pairs = [(c, a) for c, a in zip(categories, amounts) if a > 0]
    if not pairs:
        pairs = [("No Data", 1)]
    cats, amts = zip(*pairs)
    pull = [0.05] + [0] * (len(cats) - 1)
    fig = go.Figure(go.Pie(
        labels=cats, values=amts,
        hole=0.6,
        pull=pull,
        marker=dict(colors=COLORS, line=dict(color="rgba(0,0,0,0.3)", width=2)),
        textfont=dict(size=12),
        hovertemplate="%{label}<br>₹%{value:,.0f} (%{percent})<extra></extra>",
    ))
    fig.update_layout(showlegend=True)
    _base_layout(fig, "Expense Breakdown")
    return fig


def savings_allocation_pie(goal_names, contributions) -> go.Figure:
    pairs = [(n, c) for n, c in zip(goal_names, contributions) if c > 0]
    if not pairs:
        pairs = [("No Goals", 1)]
    names, contribs = zip(*pairs)
    fig = go.Figure(go.Pie(
        labels=names, values=contribs,
        hole=0.5,
        marker=dict(colors=COLORS[:len(names)], line=dict(color="rgba(0,0,0,0.3)", width=2)),
        hovertemplate="%{label}<br>₹%{value:,.0f}/month (%{percent})<extra></extra>",
    ))
    _base_layout(fig, "Savings Allocation")
    return fig


def monthly_snapshot_line(months, savings_rates) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=savings_rates,
        mode="lines+markers",
        name="Savings Rate %",
        line=dict(color=VIOLET, width=3),
        marker=dict(size=8, color=VIOLET),
        fill="tozeroy",
        fillcolor="rgba(124,58,237,0.15)",
    ))
    # 20% benchmark line
    fig.add_hline(y=20, line_dash="dash", line_color=EMERALD,
                  annotation_text="20% target", annotation_position="top right")
    _base_layout(fig, "Monthly Savings Rate Trend")
    return fig


def sip_projection_area_chart(years, invested_values, corpus_values) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=invested_values,
        name="Amount Invested",
        fill="tozeroy", fillcolor=f"rgba(6,182,212,0.15)",
        line=dict(color=CYAN, width=2),
        hovertemplate="Year %{x}<br>Invested: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=years, y=corpus_values,
        name="Projected Corpus",
        fill="tonexty", fillcolor=f"rgba(124,58,237,0.2)",
        line=dict(color=VIOLET, width=3),
        hovertemplate="Year %{x}<br>Corpus: ₹%{y:,.0f}<extra></extra>",
    ))
    _base_layout(fig, "SIP Wealth Projection")
    return fig


def loan_balance_chart(months, balance_without, balance_with) -> go.Figure:
    fig = go.Figure()
    month_labels = list(range(len(balance_without)))
    fig.add_trace(go.Scatter(
        x=month_labels, y=balance_without,
        name="Without Prepayment",
        line=dict(color=AMBER, width=2, dash="dash"),
        hovertemplate="Month %{x}<br>Balance: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=month_labels[:len(balance_with)], y=balance_with,
        name="With Prepayment",
        line=dict(color=EMERALD, width=3),
        hovertemplate="Month %{x}<br>Balance: ₹%{y:,.0f}<extra></extra>",
    ))
    _base_layout(fig, "Loan Balance Comparison")
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Outstanding (₹)")
    return fig


def income_expense_gauge(expense_pct: float) -> go.Figure:
    if expense_pct < 60:
        bar_color = EMERALD
    elif expense_pct < 80:
        bar_color = AMBER
    else:
        bar_color = RED

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=expense_pct,
        number=dict(suffix="%", font=dict(size=36, color="white")),
        delta=dict(reference=70, increasing=dict(color=RED), decreasing=dict(color=EMERALD),
                   suffix="% vs 70% target"),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="rgba(255,255,255,0.3)"),
            bar=dict(color=bar_color, thickness=0.25),
            bgcolor="rgba(255,255,255,0.05)",
            borderwidth=0,
            steps=[
                dict(range=[0, 60],   color="rgba(16,185,129,0.15)"),
                dict(range=[60, 80],  color="rgba(245,158,11,0.15)"),
                dict(range=[80, 100], color="rgba(239,68,68,0.15)"),
            ],
            threshold=dict(line=dict(color=AMBER, width=3), thickness=0.75, value=70),
        ),
        title=dict(text="Expense-to-Income Ratio", font=dict(color="rgba(255,255,255,0.7)", size=14)),
    ))
    _base_layout(fig)
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    return fig


def net_worth_donut(asset_names, asset_values, liability_names, liability_values) -> go.Figure:
    fig = go.Figure()
    # Assets — left half of pie concept using two pies side-by-side
    a_pairs = [(n, v) for n, v in zip(asset_names, asset_values) if v > 0]
    l_pairs = [(n, v) for n, v in zip(liability_names, liability_values) if v > 0]

    if a_pairs:
        a_names, a_vals = zip(*a_pairs)
    else:
        a_names, a_vals = ["No Assets"], [1]

    if l_pairs:
        l_names, l_vals = zip(*l_pairs)
    else:
        l_names, l_vals = ["No Liabilities"], [1]

    fig.add_trace(go.Pie(
        labels=a_names, values=a_vals, hole=0.55,
        name="Assets", domain=dict(x=[0, 0.45]),
        marker=dict(colors=[EMERALD, CYAN, GOLD, VIOLET]),
        title=dict(text="Assets", font=dict(size=13)),
        hovertemplate="%{label}<br>₹%{value:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Pie(
        labels=l_names, values=l_vals, hole=0.55,
        name="Liabilities", domain=dict(x=[0.55, 1.0]),
        marker=dict(colors=[RED, AMBER, "#ec4899"]),
        title=dict(text="Liabilities", font=dict(size=13)),
        hovertemplate="%{label}<br>₹%{value:,.0f}<extra></extra>",
    ))
    _base_layout(fig, "Net Worth Breakdown")
    return fig


def fte_comparison_bar(intern_data: dict, fte_data: dict) -> go.Figure:
    categories = ["Income", "Expenses", "Net Savings"]
    intern_vals = [intern_data.get("income", 0), intern_data.get("expenses", 0), intern_data.get("savings", 0)]
    fte_vals    = [fte_data.get("income", 0),   fte_data.get("expenses", 0),   fte_data.get("savings", 0)]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Internship", x=categories, y=intern_vals, marker_color=CYAN,   opacity=0.85))
    fig.add_trace(go.Bar(name="FTE",        x=categories, y=fte_vals,    marker_color=VIOLET, opacity=0.85))
    fig.update_layout(barmode="group")
    _base_layout(fig, "Internship vs FTE Comparison")
    return fig


def amortization_stacked_bar(yearly_schedule: list) -> go.Figure:
    years       = [row["year"]      for row in yearly_schedule]
    principals  = [row["principal"] for row in yearly_schedule]
    interests   = [row["interest"]  for row in yearly_schedule]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Principal Paid", x=years, y=principals, marker_color=VIOLET,  opacity=0.85))
    fig.add_trace(go.Bar(name="Interest Paid",  x=years, y=interests,  marker_color=AMBER,   opacity=0.85))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Amount (₹)")
    _base_layout(fig, "Annual Principal vs Interest Breakdown")
    return fig


def rate_history_line(dates, rates) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=rates,
        mode="lines+markers+text",
        name="Interest Rate",
        line=dict(color=VIOLET, width=3, shape="hv"),
        marker=dict(size=10, color=VIOLET, line=dict(color="white", width=2)),
        text=[f"{r:.2f}%" for r in rates],
        textposition="top center",
        textfont=dict(color="rgba(255,255,255,0.8)", size=11),
        hovertemplate="%{x}<br>Rate: %{y:.3f}%<extra></extra>",
    ))
    _base_layout(fig, "Interest Rate History")
    fig.update_yaxes(title_text="Rate (%)", tickformat=".2f")
    return fig


def wealth_path_chart(months_intern, wealth_intern, months_fte, wealth_fte) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months_intern, y=wealth_intern,
        name="Internship path",
        line=dict(color=CYAN, width=2, dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=months_fte, y=wealth_fte,
        name="FTE path",
        line=dict(color=VIOLET, width=3),
        fill="tonexty", fillcolor="rgba(124,58,237,0.1)",
    ))
    _base_layout(fig, "5-Year Wealth Projection")
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Accumulated Wealth (₹)")
    return fig
