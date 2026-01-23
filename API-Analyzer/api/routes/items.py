from fastapi import APIRouter, status
from schemas.item import ItemCreate, ItemResponse


router = APIRouter(prefix="/items", tags=["Items"])

fake_db_item = []

@router.get("/", response_model=list[ItemResponse])
def list_list():
    return fake_db_item

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item : ItemCreate):
    fake_db_item.append(item)
    return item
