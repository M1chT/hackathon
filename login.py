from hmac import new
import streamlit as st

# functions
def logout():
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.rerun()

# other pages
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
new_chat = st.Page("pages/st_newchat.py", title="New Chat", icon=":material/chat:", default=True)

st.set_page_config(page_title="Login | Marketing Tool", page_icon="🔒", layout="centered")

if not st.session_state.get("logged_in"):
    # --- Logo/Title ---
    st.markdown("""
    <div style='text-align:center; margin-bottom: 2rem;'>
        <h1 style='color:#764ba2; margin-bottom:0.5rem;'>Login</h1>
        <span style='color:#667eea; font-size:1.2rem;'>Discover your marketing strategy ⭐</span>
    </div>
    """, unsafe_allow_html=True)

    # --- Login Form ---
    with st.form("login_form", clear_on_submit=False):
        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        login_btn = st.form_submit_button("Login", type="primary")

    if login_btn:
        if not email or not password:
            st.error("Please enter both email and password.")
        elif email == "demo@demo.com" and password == "demo123":
            st.session_state["user"] = email
            st.session_state["logged_in"] = True
            st.success("Login successful! (Demo credentials)")
            st.rerun()
        else:
            st.error("Invalid email or password.")

    # --- Guest Login Button ---
    guest_btn = st.button("Continue as Guest", type="secondary")
    if guest_btn:
        st.success("Logged in as Guest?")
        st.session_state["user"] = "guest"
        st.session_state["logged_in"] = True
        st.rerun()

    # --- Sign up link ---
    st.markdown("""
    <div style='text-align:center; margin-top:2rem;'>
        <span>Don't have an account?</span>
        <a href="#" style='color:#764ba2; text-decoration:underline; margin-left:0.5rem;'>Sign up</a>
    </div>
    """, unsafe_allow_html=True)
else:
    # --- Show navigation/pages ---
    pg = st.navigation(
        {
            "Account": [logout_page],
            "Pages": [new_chat],
        }
    )
    pg.run() 