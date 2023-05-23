from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends
from jose import jwt

import src
from src.config import get_settings
from src.database.user_db import UserDAO
from src.schemas.users import User


class JwtConverter:
    def __init__(self, userdao: UserDAO, config: Annotated[src.config.SecuritySetting, Depends(get_settings)]):
        self.dao = userdao
        self.secret = config.jwt_secret

    def get_user(self, token: str) -> User | None:
        decoded = jwt.decode(token, self.secret)
        username = decoded.get("username")
        user = self.dao.get_user_by_username(username=username)
        return User.from_orm(user)
    def get_jwt(self, user: User):
        claims = {
            "iss": "ska_checklist",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "username": user.username,
            "is_superuser": user.is_superuser,
        }
        return jwt.encode(claims=claims, key=self.secret)
