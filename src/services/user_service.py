# src/services/user_service.py
import re
from src.dao.User_dao import UserDAO  
from src.dao.Subscription_dao import SubscriptionDAO

class UserService:
    def __init__(self):
        self.user_dao = UserDAO()
        self.subscription_dao = SubscriptionDAO()

    def is_valid_email(self, email: str) -> bool:
        
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def add_user(self):
        
        name = input("Enter the Name of the user: ").strip()
        
        while True:
            email = input("Enter the Email-ID of the user: ").strip()
            
            
            if not self.is_valid_email(email):
                print("Invalid email format. Please enter a valid email.")
                continue
            
            
            if self.user_dao.get_user_by_email(email):
                print("Email already exists. Please enter a different email.")
                continue
            
            break  
        
        
        resp=self.user_dao.create_user(name, email)
        if(resp):
            print(f"User '{name}' with email '{email}' added successfully!")
        else:
            print("User not created")

    def list_users(self):
        
        users = self.user_dao.get_all_users() 
        
        if not users:
            print("No users found.")
            return
        
        print("\n=== Registered Users ===")
        print(f"{'ID':<5} {'Name':<25} {'Email'}")
        print("-" * 50)
        for user in users:
            print(f"{user['id']:<5} {user['name']:<25} {user['email']}")
        print("-" * 50)

    
    def delete_user(self):
        user_id = input("Enter the User ID to delete: ").strip()
        if not user_id.isdigit():
            print("Invalid User ID.")
            return
        user_id = int(user_id)

        # Step 1: Verify user exists
        user = self.user_dao.get_user_by_id(user_id)
        if not user:
            print(f"❌ User ID {user_id} does not exist.")
            return

        # Step 2: Check if user has any subscriptions
        subs = self.subscription_dao.get_subscriptions_by_user(user_id)
        if subs:
            print(f"⚠️ Cannot delete User ID {user_id} — they still have subscriptions.")
            return

        # Step 3: Delete the user
        success = self.user_dao.delete_user(user_id)
        if success:
            print(f"✅ User ID {user_id} deleted successfully.")
        else:
            print(f"❌ Failed to delete User ID {user_id}.")
