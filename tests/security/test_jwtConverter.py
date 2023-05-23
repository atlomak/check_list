from datetime import datetime, timedelta

import pytest
from jose import jwt, JWTError

from src.config import SecuritySetting
from src.schemas.users import User
from src.security.JwtConverter import JwtConverter

exp_time = timedelta(minutes=15)
test_secret = "yqWlVAiIgqm1nqc5SEa1aM7C6lJ8JTrZ"


@pytest.fixture
def get_jwt():
    claims = {
        "iss": "ska_checklist",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + exp_time,
        "username": "test_user",
        "is_superuser": "true"
    }
    return jwt.encode(claims=claims, key=test_secret)

@pytest.fixture
def get_exp_jwt():
    claims = {
        "iss": "ska_checklist",
        "iat": datetime.utcnow() - timedelta(minutes=16),
        "exp": datetime.utcnow() - timedelta(minutes=1),
        "username": "test_user",
        "is_superuser": "true"
    }
    return jwt.encode(claims=claims, key=test_secret)
@pytest.fixture
def get_dummy_config():
    return SecuritySetting(jwt_secret=test_secret)

@pytest.fixture
def get_user() -> User:
    return User(id=1,
                is_superuser = True,
                created_at = datetime.utcnow(),
                username="test_user",
                name="John",
                surname="Doe",
                )

@pytest.fixture
def converter(get_dummy_config, get_dummy_dao) -> JwtConverter:
    return JwtConverter(userdao=get_dummy_dao, config=get_dummy_config)


def test_exchange_jwt_to_user(get_jwt, converter: JwtConverter):
    user: User = converter.get_user(get_jwt)

    assert user.username == "test_user"
    assert user.name == "John"

def test_expired_jwt(get_exp_jwt, converter: JwtConverter):
    with pytest.raises(JWTError):
        user: User = converter.get_user(get_exp_jwt)

def test_wrong_jwt_signature(converter):
    with pytest.raises(JWTError):
        user: User = converter.get_user("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")

def test_exchange_user_to_jwt(get_user, converter):
    token = converter.get_jwt(get_user)

    decoded = jwt.decode(token=token, key=test_secret)

    assert decoded.get("username") == "test_user"
    assert decoded.get("is_superuser") == True