import streamlit as st
import bcrypt
from supabase import create_client

# Load Supabase credentials from secrets.toml
supabase_url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
supabase_key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]

# Initialize Supabase client
supabase = create_client(supabase_url, supabase_key)


def login(username: str, password: str) -> bool:
    """Authenticate user and store session if successful"""
    response = supabase.table("users").select("*").eq("username", username).execute()
    if response.data:
        user = response.data[0]
        if bcrypt.checkpw(password.encode(), user["password"].encode()):
            st.session_state["user"] = user
            return True
    return False



def signup(username: str, password: str):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        response = supabase.table("users").insert({
            "username": username,
            "password": hashed
        }).execute()
        # response.data contains your inserted row(s)
        return {
            "data": response.data,
            "error": None
        }
    except Exception as e:
        return {
            "data": None,
            "error": str(e)
        }



def logout():
    """Clear user session"""
    if "user" in st.session_state:
        del st.session_state["user"]


def is_authenticated() -> bool:
    """Check if user is logged in"""
    return "user" in st.session_state
