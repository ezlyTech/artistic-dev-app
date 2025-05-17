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
    try:
        response = supabase.table("users").select("*").eq("username", username).execute()
        if response.data:
            user = response.data[0]
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                st.session_state["user"] = user
                return True
    except Exception as e:
        st.error(f"Login failed: {e}")
    return False

def signup(username: str, password: str) -> bool:
    """Create a new user account with hashed password"""
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        response = supabase.table("users").insert({
            "username": username,
            "password": hashed_pw
        }).execute()
        return response.data is not None
    except Exception as e:
        st.error(f"Signup failed: {e}")
        return False

def logout():
    """Clear user session"""
    st.session_state.pop("user", None)

def is_authenticated() -> bool:
    """Check if user is logged in"""
    return "user" in st.session_state
