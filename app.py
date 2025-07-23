import streamlit as st
from utils.auth import login_user
from utils.database import setup_database
# --- THIS IS THE CRUCIAL LINE ---
from dotenv import load_dotenv

from utils.database import get_user, setup_database

# --- AND THIS LINE MUST BE AT THE TOP ---
load_dotenv() 
# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Balance Sheet AI Analyzer",
    page_icon="📊",
    layout="centered"
)

# --- DATABASE SETUP ---
# This will create the DB and tables if they don't exist
# and populate with initial data.
setup_database()

# --- LOGIN LOGIC ---
st.title("📊 Balance Sheet AI Analyzer")
st.write("Please log in to continue.")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

    if submitted:
        user = login_user(username, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user[0]
            st.session_state["username"] = user[1]
            st.session_state["role"] = user[3]
            st.success(f"Welcome, {st.session_state['username']}!")
            st.rerun() # Use rerun to immediately navigate after login
        else:
            st.error("Invalid username or password.")

# --- MAIN APP DISPLAY AFTER LOGIN ---
if "logged_in" in st.session_state and st.session_state["logged_in"]:
    st.sidebar.success(f"Logged in as {st.session_state['username']} ({st.session_state['role']})")

    st.header("Welcome to the Dashboard!")
    st.write("Navigate using the sidebar to access different features.")
    st.info("👈 Select a page from the sidebar to get started.", icon="ℹ️")

    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
else:
    st.info("Please enter your credentials to access the application.")