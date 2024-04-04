from core.security import is_unauthorized_url
from fastapi import status
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
import crud
from db.database import SessionLocal
from services.user_service import decode_access_token, get_user_by_email_active


class AuthMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if is_unauthorized_url(request):
            return await call_next(request)

        token = request.headers.get("Authorization", None)
        print(token)
        if token == None:
            return JSONResponse(
                content={"detail": "Authentication header missing"},
                status_code=(status.HTTP_401_UNAUTHORIZED),
            )
        claim = decode_access_token(token)
        if claim == None:
            return JSONResponse(
                content={"detail": "Please check authentication token."},
                status_code=(status.HTTP_401_UNAUTHORIZED),
            )
        user_id = claim.get("id", None)
        if user_id == None:
            return JSONResponse(
                content={"detail": "Please check authentication token."},
                status_code=(status.HTTP_401_UNAUTHORIZED),
            )
        db = None
        try:
            try:
                db = SessionLocal()
                user = crud.user.get_by_id(db=db, id=user_id)
                if not user:
                    return JSONResponse(
                        content={"detail": "User not found."},
                        status_code=(status.HTTP_404_NOT_FOUND),
                    )
                request.state.current_user = user
            except Exception as e:
                raise e

        finally:
            if db != None:
                db.close()

        return await call_next(request)
