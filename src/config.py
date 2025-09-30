import streamlit as st
from supabase import create_client, Client # type: ignore

def get_supabase() -> Client:
    """
    Creates and returns a Supabase client using credentials
    stored in Streamlit's secrets manager.
    """
    # Get the Supabase URL and Key from st.secrets
    url = st.secrets.get("supabase", {}).get("url")
    key = st.secrets.get("supabase", {}).get("key")

    # Raise an error if the credentials are not found
    if not url or not key:
        raise RuntimeError(
            "Supabase credentials not found. "
            "Please set them in your Streamlit secrets."
        )

    # Initialize and return the Supabase client
    return create_client(url, key)