import re
from typing import Dict

class AuthenticationSystem:
    def __init__(self):
        self.users = {
            "admin": "1234",
        }

    def login(self, username: str, password: str) -> bool:
        if username in self.users and self.users[username] == password:
            return True
        raise ValueError("Invalid Credentials")

    def logout(self, user_id: int):
        print(f"user {user_id} logged out")

    def validate_session(self, token: str) -> bool:
        return re.match("^[a-zA-Z0-9]{6,}$", token) is not None

def authenticate_system():
    auth = AuthenticationSystem()
    
    try:
        if(auth.login('admin','1234')):
            print("Authentication successful")
            
        else:
            print("Invalid Credentials")
            
    except ValueError as e:
        print(f"{e}")
        
    print(auth.validate_session("abcdfg"))
    return True


if __name__ == "__main__":
    authenticate_system()