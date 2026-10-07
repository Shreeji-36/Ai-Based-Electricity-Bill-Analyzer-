from sqlalchemy import select
from app import config
from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import User


def init_db() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.email == config.ADMIN_EMAIL)):
            db.add(User(email=config.ADMIN_EMAIL, name="Administrator",
                        password_hash=hash_password(config.ADMIN_PASSWORD), role="admin"))
            db.commit()