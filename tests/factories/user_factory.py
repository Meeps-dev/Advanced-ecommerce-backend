import uuid


def make_user_payload(role: str = "customer") -> dict:
    return {
        "email": f"factory_{uuid.uuid4().hex}@example.com",
        "password": "StrongPass123!",
        "full_name": f"Factory {role.title()} User",
    }
