from pydantic import BaseModel, ConfigDict, Field


class PasswordChangeSchema(BaseModel):
    old_password: str
    new_password: str = Field(
        min_length=8, description="Password should be at least 8 characters long"
    )

    model_config = ConfigDict(from_attributes=True)
