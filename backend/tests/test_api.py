import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.security.auth import authenticate_user, create_access_token, decode_token


def test_authentication():
    user = authenticate_user("admin", "admin123")
    assert user is not None
    assert user.username == "admin"
    user = authenticate_user("admin", "wrong")
    assert user is None


def test_token_creation():
    user = authenticate_user("analyst", "analyst123")
    token = create_access_token({"sub": user.username, "role": user.role})
    assert token is not None
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded.username == "analyst"


def test_rbac():
    from app.security.auth import has_permission
    assert has_permission("admin", "manage_users") is True
    assert has_permission("viewer", "write") is False
    assert has_permission("analyst", "investigate") is True
