import os

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "120"))
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "orewashreeji36@gmail.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Shreeji@123")