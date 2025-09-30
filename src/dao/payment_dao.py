from typing import List, Dict
from src.config import get_supabase

class PaymentsDAO:
    def __init__(self):
        self._sb = get_supabase()  # internal Supabase client

    def insert_payment(self, subscription_id: int, amount: float, method: str, status: str):
        payload = {
            "subscription_id": subscription_id,
            "amount": amount,
            "payment_date": "now()",  
            "method": method,
            "status": status
        }
        resp = self._sb.table("payments").insert(payload).execute()
        return resp.data if resp.data else None

    def get_payments_by_subscription(self, subscription_id: int) -> List[Dict]:
        resp = self._sb.table("payments").select("*").eq("subscription_id", subscription_id).execute()
        return resp.data if resp.data else []

    def get_total_spend_for_subscriptions(self, subscription_ids: List[int]) -> float:
        if not subscription_ids:
            return 0.0

        resp = (
            self._sb.table("payments")
            .select("amount")
            .in_("subscription_id", subscription_ids)
            .eq("status", "completed")  # must match actual status value
            .execute()
        )

        if not resp.data:
            return 0.0


        return sum(float(row["amount"]) for row in resp.data)


    def get_all_payments(self):
        resp = self._sb.table("payments").select("*").execute()
        return resp.data if resp.data else []