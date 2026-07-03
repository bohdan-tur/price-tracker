from pydantic import BaseModel, ConfigDict


class RefreshTokenRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict(from_attributes=True)
