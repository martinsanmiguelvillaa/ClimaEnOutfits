from pydantic import BaseModel

class OutfitResponse(BaseModel):
    upper_body: str
    lower_body: str
    footwear: str
    extras: list[str]
    summary: str