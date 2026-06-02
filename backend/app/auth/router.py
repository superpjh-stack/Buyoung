from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import LoginRequest, RefreshRequest, TokenResponse, UserOut
from app.auth.service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.auth.dependencies import get_current_user
from app.common.response import ok
from app.common.exceptions import MESException
from app.config import settings
from app.database import get_db

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, body.username, body.password)
    token_data = {"sub": str(user.user_id)}
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserOut.model_validate(user),
    }


@router.post("/refresh")
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise MESException(401, "UNAUTHORIZED", "리프레시 토큰이 필요합니다.")
    token_data = {"sub": payload["sub"]}
    return ok({
        "access_token": create_access_token(token_data),
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    })


@router.post("/logout")
async def logout(current_user=Depends(get_current_user)):
    # 실서비스에서는 Redis에 refresh_token 블랙리스트 추가
    return ok({"message": "로그아웃 되었습니다."})


@router.get("/me", response_model=UserOut)
async def me(current_user=Depends(get_current_user)):
    return current_user
