import streamlit as st


def render_top_nav():
    """Global top navigation bar to switch between main sections."""
    st.markdown(
        "<div class='section-header'>🔗 Quick Navigation</div>",
        unsafe_allow_html=True,
    )

    nav_cols = st.columns(5)
    nav_items = [
        ("🏠", "Home",     "app.py"),
        ("💰", "Income",   "pages/2_💰_Income.py"),
        ("💳", "Expenses", "pages/3_💳_Expenses.py"),
        ("🎯", "Savings",  "pages/4_🎯_Savings_Goals.py"),
        ("🏦", "Loans",    "pages/5_🏦_Loan_Manager.py"),
    ]

    for col, (icon, title, path) in zip(nav_cols, nav_items):
        with col:
            if st.button(f"{icon} {title}", key=f"topnav_{title}", use_container_width=True):
                st.switch_page(path)

    st.markdown("---", unsafe_allow_html=True)
