# src/services/user_service.py
import re
from dao.User_dao import UserDAO  

class UserService:
    def __init__(self):
        self.user_dao = UserDAO()

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
