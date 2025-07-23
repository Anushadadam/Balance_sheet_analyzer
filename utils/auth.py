import streamlit as st
from .database import get_user

def check_login():
    """Checks if a user is logged in. If not, stops the script and shows a message."""
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("You must be logged in to access this page.")
        st.stop()

def check_role_access(allowed_roles):
    """Checks if the logged-in user's role is in the list of allowed roles."""
    check_login()
    user_role = st.session_state.get("role")
    if user_role not in allowed_roles:
        st.error(f"Access Denied. Your role ('{user_role}') does not have permission to view this page.")
        st.stop()


def login_user(username, password):
    """Validates user credentials against the database."""
    user = get_user(username)
    if user and user['password'] == password:
        return user
    return None

def logout_button():
    """Renders a logout button in the sidebar."""
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()