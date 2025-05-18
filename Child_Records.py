import streamlit as st
from utils.auth import get_supabase_admin_client
import re

def is_valid_uuid(val):
    uuid_regex = re.compile(
        r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )
    return bool(uuid_regex.match(val))

def render_child_records(child_id: str):
    if not child_id:
        st.error("No child ID provided.")
        return

    if not is_valid_uuid(child_id):
        st.error("Invalid child ID.")
        return

    supabase_admin = get_supabase_admin_client()
    user_id = st.session_state['user']['id']

    child_resp = supabase_admin.table("children").select("name").eq("id", child_id).eq("user_id", user_id).execute()
    if not child_resp.data:
        st.error("Child record not found or access denied.")
        return

    child_name = child_resp.data[0]["name"]
    st.title(f"Records for {child_name}")

    results_resp = supabase_admin.table("results").select("*").eq("child_id", child_id).order("created_at", desc=True).execute()
    results = results_resp.data if results_resp.data else []

    if not results:
        st.info("No analysis records found for this child.")
    else:
        for record in results:
            st.markdown("---")
            st.image(record["image_path"], caption=f"Prediction: {record['prediction']} (Confidence: {record['confidence']:.2f}%)", use_container_width=True)

    st.markdown("---")
    if st.button("⬅️ Back to Analyze"):
        st.session_state.pop('selected_child_id', None)
        st.rerun()
