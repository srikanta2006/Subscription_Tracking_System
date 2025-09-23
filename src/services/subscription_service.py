# src/services/subscription_service.py

from src.dao.Subscription_dao import SubscriptionDAO
from src.dao.default_subscription_dao import DefaultSubscriptionDAO
from src.dao.User_dao import UserDAO
from src.dao.payment_dao import PaymentsDAO

class SubscriptionService:
    def __init__(self):
        self.subscription_dao = SubscriptionDAO()
        self.default_dao = DefaultSubscriptionDAO()
        self.user_dao = UserDAO()
        self.payment_dao = PaymentsDAO()

    def add_subscription_for_user(self):
        user_id = input("Enter the User ID to add subscription for: ").strip()
        if not user_id.isdigit():
            print("Invalid User ID.")
            return
        user_id = int(user_id)

       
        default_subs = self.default_dao.get_all_default_subscriptions()
        print("\n--- Default Subscriptions ---")
        for i, sub in enumerate(default_subs, 1):
            print(f"{i}. {sub['name']} (Plan: {sub['plan_type']}, Cost: {sub['cost']})")
        print(f"{len(default_subs)+1}. Add Custom Subscription")

        
        choice = input("Select a subscription by number: ").strip()
        if not choice.isdigit():
            print("Invalid choice.")
            return
        choice = int(choice)

        if 1 <= choice <= len(default_subs):
            sub_name = default_subs[choice-1]['name']
            plan_type = default_subs[choice-1]['plan_type']
            cost = default_subs[choice-1]['cost']
        elif choice == len(default_subs)+1:
            sub_name = input("Enter the name of your subscription: ").strip()
            plan_type = input("Enter the plan type (monthly/yearly): ").strip()
            cost_input = input("Enter the cost: ").strip()
            try:
                cost = float(cost_input)
            except ValueError:
                print("Invalid cost.")
                return

            # Add custom subscription to master list
            self.default_dao.add_default_subscription(sub_name, plan_type, cost)
            print(f"Added '{sub_name}' to master subscription list.")
        else:
            print("Invalid choice.")
            return

        # Step 4: Get subscription dates
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()

        # Step 5: Save user-specific subscription
        self.subscription_dao.add_subscription(
            user_id=user_id,
            name=sub_name,
            plan_type=plan_type,
            cost=cost,
            start_date=start_date,
            end_date=end_date,
            status="Active"
        )
        print(f"Subscription '{sub_name}' added for user ID {user_id}.")
    
    def view_subscriptions_for_user(self):
    # Step 1: Get User ID
        user_id = input("Enter the User ID to view subscriptions for: ").strip()
        if not user_id.isdigit():
            print("Invalid User ID.")
            return
        user_id = int(user_id)

        # Step 1b: Verify user exists
        if not self.user_dao.get_user_by_id(user_id):
            print(f"User ID {user_id} does not exist.")
            return

    # Step 2: Fetch subscriptions for the user only
        subs = self.subscription_dao.get_subscriptions_by_user(user_id)

    # Step 3: Display subscriptions
        if not subs:
            print(f"No subscriptions found for user ID {user_id}.")
            return

        print(f"\n--- Subscriptions for User ID {user_id} ---")
        print(f"{'No.':<5} {'Name':<25} {'Plan':<10} {'Cost':<10} {'Start Date':<12} {'End Date':<12} {'Status'}")
        print("-" * 90)
        for i, sub in enumerate(subs, 1):
            print(f"{i:<5} {sub['name']:<25} {sub['plan_type']:<10} {sub['cost']:<10} {sub['start_date']:<12} {sub['end_date']:<12} {sub['status']}")
        print("-" * 90)

    def is_valid_user(self, user_id: int) -> bool:
        user = self.user_dao.get_user_by_id(user_id)
        return user is not None
    
    def calculate_total_spend(self):
        # Step 1: Get User ID
        user_id = input("Enter the User ID: ").strip()
        if not user_id.isdigit():
            print("Invalid User ID.")
            return
        user_id = int(user_id)

        # Step 2: Check if user exists
        user = self.user_dao.get_user_by_id(user_id)
        if not user:
            print(f"❌ User ID {user_id} does not exist.")
            return

        # Step 3: Get payments for all subscriptions of this user
        subs = self.subscription_dao.get_subscriptions_by_user(user_id)
        if not subs:
            print(f"⚠️ User ID {user_id} has no subscriptions.")
            return

        sub_ids = [s["id"] for s in subs]
        total = self.payment_dao.get_total_spend_for_subscriptions(sub_ids)

        print(f"\n💰 Total Spend for User ID {user_id} ({user['name']}): {total:.2f}")
