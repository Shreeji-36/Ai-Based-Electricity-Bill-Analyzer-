from app import config
from app.core.security import hash_password

USERS: dict[str, dict] = {}


def seed_admin() -> None:
    USERS[config.ADMIN_EMAIL] = {
        "email": config.ADMIN_EMAIL,
        "name": "Administrator",
        "password": hash_password(config.ADMIN_PASSWORD),
        "role": "admin",
    }