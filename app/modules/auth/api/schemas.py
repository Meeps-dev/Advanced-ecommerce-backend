from pydantic import BaseModel, ConfigDict, EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class MessageResponse(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)
