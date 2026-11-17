from pydantic import BaseModel, Field
from .models import Role


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=6, max_length=72)


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"