from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service
from app.core.dependencies import get_app_name

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserCreate
)
def create_user(user:UserCreate, app_name: str = Depends(get_app_name)):
    return user_service.create_user(user)

@router.get("/", response_model=list[UserResponse])
def list_users():
    return user_service.get_all_users()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

