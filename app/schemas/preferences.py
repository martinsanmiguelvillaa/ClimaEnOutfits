from pydantic import BaseModel, Field


class PreferenceBody(BaseModel):
    preferences: str = Field(min_length=1, max_length=300)
