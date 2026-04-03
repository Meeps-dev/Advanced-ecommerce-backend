from app.core.security import hash_password, verify_password, create_access_token


def test_hash_and_verify_password():
    pwd = "StrongPass123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "123"})
    assert isinstance(token, str)
    assert len(token) > 20
