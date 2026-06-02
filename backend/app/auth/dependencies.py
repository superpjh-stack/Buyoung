from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import decode_token
from app.common.exceptions import MESException, ForbiddenError
from app.database import get_db

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    from app.domains.system.models import User

    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise MESException(401, "UNAUTHORIZED", "액세스 토큰이 필요합니다.")

    user_id = payload.get("sub")
    result = await db.execute(
        select(User).where(User.user_id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise MESException(401, "UNAUTHORIZED", "사용자를 찾을 수 없습니다.")
    return user


def require_role(*roles: str):
    async def checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise ForbiddenError()
        return current_user
    return checker
