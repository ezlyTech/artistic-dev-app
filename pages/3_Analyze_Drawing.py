import streamlit as st
from utils.auth import is_authenticated

if not is_authenticated():
    st.warning("Please log in first.")
    st.page_link("main.py", label="Go to Login", icon="🔒")
    st.stop()

st.title("Analyze Child's Drawing")

# Your drawing analysis logic goes here
