import streamlit as st
from utils.auth import signup

st.title("Create Account")

username = st.text_input("Username")
password = st.text_input("Password", type="password")
confirm = st.text_input("Confirm Password", type="password")

if st.button("Sign Up"):
    if not username:
        st.error("Please enter a username.")
    elif not password or not confirm:
        st.error("Please enter and confirm your password.")
    elif password != confirm:
        st.error("Passwords do not match.")
    else:
        res = signup(username, password)
        st.write("Signup response:", res)  # Debug output to see exact response

        if res["data"]:
            st.success("Account created! Go to the login page.")
            st.markdown("[Login Page](app.py)")
        elif res["error"]:
            st.error(f"Failed to create account: {res['error']}")
        else:
            st.error("Failed to create account due to an unknown error.")

