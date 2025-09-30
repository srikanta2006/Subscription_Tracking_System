from typing import Optional, List, Dict
from src.config import get_supabase

class SubscriptionDAO:
    def __init__(self):
        self._sb = get_supabase()

    def add_subscription(self, user_id:int, name:str, plan_type : str, cost: float, start_date: str,end_date: str ,status: str ="Active"):
        payload = {
            "user_id": user_id,
            "name": name,
            "plan_type": plan_type,
            "cost": cost,
            "start_date": start_date,
            "end_date": end_date,
            "status": "Active"
        }

        self._sb.table("subscriptions").insert(payload).execute()

    def get_subscriptions_by_user(self, user_id: int):
        resp = self._sb.table("subscriptions").select("*").eq("user_id", user_id).execute()
        return resp.data if resp.data else []
        
    
    def get_subscription_by_id(self, subscription_id: int):
        resp = self._sb.table("subscriptions").select("*").eq("id", subscription_id).single().execute()
        return resp.data if resp.data else None
    
    def get_all_subscriptions(self):
        resp = self._sb.table("subscriptions").select("*").execute()
        return resp.data if resp.data else []