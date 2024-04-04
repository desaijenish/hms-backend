
from db.database import SessionLocal
from fastapi import Request

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request):
    return request.state.current_user
