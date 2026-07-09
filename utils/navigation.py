import streamlit as st

import streamlit as st

def check_password():
    """Block page if password not entered. Call at top of every page."""
    if st.session_state.get("pw_ok"):
        return  # ✅ Already unlocked

    # Hide sidebar
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    st.title("🔒 FinTrack — Private Access")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.5);margin-bottom:1rem;'>"
        "Enter the password to access your financial dashboard.</div>",
        unsafe_allow_html=True
    )

    pw = st.text_input("Password:", type="password", key="pw_input")

    if st.button("🔓 Unlock", type="primary"):
        PASSWORD = st.secrets.get("APP_PASSWORD", "fintrack")
        if pw == PASSWORD:
            st.session_state["pw_ok"] = True
            st.rerun()
        else:
            st.error("❌ Incorrect password.")
    st.stop()


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
