from typing import Optional, List, Dict
from src.config import get_supabase

class UserDAO:
    def __init__(self):
        self._sb = get_supabase()

    def create_user(self, name: str, email: str) -> Optional[Dict]:
        payload = {"name": name, "email": email}
        
        self._sb.table("users").insert(payload).execute()
        return True


    def get_user_by_email(self,email:str) -> Optional[Dict]:
        resp = self._sb.table("users").select("*").eq("email", email).limit(1).execute()
        return resp.data[0] if resp.data else False


    def get_all_users(self):
        resp = self._sb.table("users").select("*").execute()
        return resp.data[0] if resp.data else False