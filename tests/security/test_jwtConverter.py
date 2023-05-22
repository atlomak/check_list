from datetime import datetime, timedelta

import pytest
from jose import jwt

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
def get_dummy_config():
    return SecuritySetting(jwt_secret=test_secret)


@pytest.fixture
def converter(get_dummy_config, get_dummy_dao):
    return JwtConverter(userdao=get_dummy_dao, config=get_dummy_config)


def test_exchange_jwt_to_user(get_jwt, converter):
    user: User = converter.get_user(get_jwt)

    assert user.username == "test_user"
    assert user.name == "John"
