# src/cli/main.py

from src.services.user_service import UserService
from src.services.subscription_service import SubscriptionService
from src.services.payment_service import PaymentService

class SubscriptionTrackerCLI:
    def __init__(self):
        self.user_service = UserService()
        self.subscription_service = SubscriptionService()
        self.payment_service = PaymentService()
        self.actions = {
            "1": self.user_service.add_user,
            "2": self.user_service.list_users,
            "3": self.subscription_service.add_subscription_for_user,
            "4": self.subscription_service.view_subscriptions_for_user,
            "5": self.payment_service.add_payment_for_subscription,
            "6": self.payment_service.view_payments_for_subscription,
            "7": self.user_service.delete_user,
            "8": self.subscription_service.calculate_total_spend,
            "9": self.exit_program
        }

    def print_menu(self):
        print("\n==== Subscription Tracker ====")
        print("1. Add User")
        print("2. List Users")
        print("3. Add Subscription for a User")
        print("4. View Subscriptions for a User")
        print("5. Add Payment for a Subscription")
        print("6. View Payments for a Subscription")
        print("7. Delete User")
        print("8. Total Spend of the User")
        print("9. Exit")

    def exit_program(self):
        print("Exiting Subscription Tracker. Goodbye!")
        exit(0)

    def run(self):
        while True:
            self.print_menu()
            choice = input("Enter your choice: ").strip()
            action = self.actions.get(choice)
            if action:
                action()
            else:
                print("Invalid choice. Please enter a choise between 1 and 9.")


if __name__ == "__main__":
    cli = SubscriptionTrackerCLI()
    cli.run()
