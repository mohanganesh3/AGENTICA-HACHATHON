# backend/app/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..database import get_user_collection
from ..auth import get_current_user, get_password_hash
from ..schemas import User, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    created_at: datetime

class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user account"""
    user_collection = await get_user_collection()
    
    # Check if email already exists
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user document
    user_data = user.dict()
    user_data["hashed_password"] = hashed_password
    del user_data["password"]
    user_data["created_at"] = datetime.utcnow()
    
    # Insert into database
    result = await user_collection.insert_one(user_data)
    created_user = await user_collection.find_one({"_id": result.inserted_id})
    
    return UserResponse(**created_user)

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """Get current authenticated user details"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UpdateUserRequest,
    current_user: User = Depends(get_current_user)
):
    """Update current user's information"""
    user_collection = await get_user_collection()
    update_dict = {}
    
    # Check email uniqueness if changing email
    if update_data.email and update_data.email != current_user.email:
        existing_user = await user_collection.find_one({"email": update_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        update_dict["email"] = update_data.email
    
    if update_data.full_name:
        update_dict["full_name"] = update_data.full_name
    
    if update_data.password:
        update_dict["hashed_password"] = get_password_hash(update_data.password)
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )
    
    # Perform update
    updated_user = await user_collection.find_one_and_update(
        {"_id": current_user.id},
        {"$set": update_dict},
        return_document=True
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**updated_user)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_user)
):
    """Delete current user account"""
    user_collection = await get_user_collection()
    
    # Delete user document
    result = await user_collection.delete_one({"_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"detail": "User account deleted successfully"}

# Admin-only endpoints (if needed)
@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_user)
):
    """Get all users (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    user_collection = await get_user_collection()
    users = await user_collection.find().to_list(100)
    return [UserResponse(**user) for user in users]