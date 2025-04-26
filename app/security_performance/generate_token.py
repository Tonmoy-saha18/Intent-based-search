import jwt
import datetime
import os
# from dotenv import load_dotenv

# load_dotenv()
JWT_SECRET = "SecretKey2025"
ALGORITHM = "HS256"

def generate_jwt_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

# Example usage
if __name__ == "__main__":
    admin_token = generate_jwt_token("admin_user", "admin")
    user_token = generate_jwt_token("regular_user", "user")
    print(f"Admin Token: {admin_token}")
    print(f"User Token: {user_token}")