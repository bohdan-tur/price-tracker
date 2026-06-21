from pydantic import BaseModel, Field


class PasswordChangeSchema(BaseModel):
    old_password: str
    new_password: str = Field(
        min_length=8, description="Password should be at least 8 characters long"
    )
