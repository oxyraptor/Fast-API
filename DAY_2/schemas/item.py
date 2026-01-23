from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    price: float = Field(..., gt=0)
    in_stock: bool = True


class ItemResponse(BaseModel):
    name: str
    price: float
    in_stock: bool

