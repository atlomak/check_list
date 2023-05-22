from src.database.user_db import UserDAO
from src.schemas.users import UserInDB
from datetime import datetime
import pytest

dummy_user = UserInDB(id=1,
                      is_superuser = True,
                      created_at = datetime.utcnow(),
                      username="test_user",
                      name="John",
                      surname="Doe",
                      password_hash="$2y$10$GiWu3faibI950otht9Qi8u4M615BSJ.CoKR7MUdH0dW7S/j74PDqW")

class FakeDAO(UserDAO):
    def __init__(self):
        pass
    def get_all_users(self) -> list[UserInDB]:
        pass
    def get_user_by_id(self, id: int) -> UserInDB | None:
        pass
    def get_user_by_username(self, username: str) -> UserInDB | None:
        if username == "test_user":
            return dummy_user
        return None
    def modify_user(self, id: int, *args, **kwargs):
        pass
    def delete_user(self, id: int):
        pass

@pytest.fixture
def get_dummy_dao() -> FakeDAO:
    return FakeDAO()