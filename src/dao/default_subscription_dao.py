from typing import Optional, List, Dict
from src.config import get_supabase

class DefaultSubscriptionDAO:
    def __init__(self):
        self._sb = get_supabase()

    def get_all_default_subscriptions(self):
        resp=self._sb.table("defaultsubscriptions").select("*").execute()
        return resp.data if resp.data else []
    
    def add_default_subscription(self, sub_name: str, plan_type : str, cost : float):
        payload = {"name": sub_name, "plan_type": plan_type, "cost": cost}
        self._sb.table("defaultsubscriptions").insert(payload).execute()
        return True