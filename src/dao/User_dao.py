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
        return resp.data if resp.data else []
    
    def get_user_by_id(self, user_id):
        resp = self._sb.table("users").select("*").eq("id", user_id).execute()
        if resp.data:
            return resp.data[0]  # returns the user dict
        return None
    
    def delete_user(self, user_id: int) -> bool:
        resp = self._sb.table("users").delete().eq("id", user_id).execute()
        return True if resp.data else False