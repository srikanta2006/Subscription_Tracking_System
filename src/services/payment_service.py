from src.dao.Subscription_dao import SubscriptionDAO
from src.dao.default_subscription_dao import DefaultSubscriptionDAO
from src.dao.User_dao import UserDAO
from src.dao.payment_dao import PaymentsDAO

class PaymentService:
    def __init__(self):
        self.subscription_dao = SubscriptionDAO()
        self.default_dao = DefaultSubscriptionDAO()
        self.user_dao = UserDAO()
        self.payment_dao = PaymentsDAO()

    def add_payment_for_subscription(self):
        try:
            subscription_id = input("Enter Subscription ID: ").strip()
            if not subscription_id.isdigit():
                print("Invalid Subscription ID.")
                return
            subscription_id = int(subscription_id)

            subscription = self.subscription_dao.get_subscription_by_id(subscription_id)
            if not subscription:
                print(f"No subscription found with ID {subscription_id}.")
                return

            amount_input = input("Enter Payment Amount: ").strip()
            try:
                amount = float(amount_input)
            except ValueError:
                print("Invalid amount entered.")
                return

            method = input("Enter Payment Method (e.g., UPI, Card, PayPal): ").strip()
            status = input("Enter Payment Status (Completed/Pending/Failed): ").strip().capitalize()
            if status not in ["Completed", "Pending", "Failed"]:
                print("Invalid status. Must be Completed, Pending, or Failed.")
                return

            result = self.payment_dao.insert_payment(subscription_id, amount, method, status)
            if result:
                print(f"✅ Payment of {amount} added for Subscription ID {subscription_id}.")
            else:
                print("⚠️ Failed to add payment.")

        except Exception as e:
            print(f"Error adding payment: {e}")

    def view_payments_for_subscription(self):
        subscription_id = input("Enter the Subscription ID to view payments: ").strip()
        if not subscription_id.isdigit():
            print("Invalid Subscription ID.")
            return
        subscription_id = int(subscription_id)

        payments = self.payment_dao.get_payments_by_subscription(subscription_id)
        if not payments:
            print(f"No payments found for subscription ID {subscription_id}.")
            return

        print(f"\n--- Payments for Subscription ID {subscription_id} ---")
        print(f"{'No.':<5} {'Amount':<10} {'Method':<15} {'Status':<12} {'Payment Date'}")
        print("-" * 70)
        for i, pay in enumerate(payments, 1):
            print(f"{i:<5} {pay['amount']:<10} {pay['method']:<15} {pay['status']:<12} {pay['payment_date']}")
        print("-" * 70)
