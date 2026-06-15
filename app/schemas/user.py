from pydantic import BaseModel, EmailStr,Field

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8,description="Password must be at least 8 characters long")

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True