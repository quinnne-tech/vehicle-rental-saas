"""Authentication API endpoints"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.schemas import RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.database.connection import get_db
from app.core.constants import UserRole, SubscriptionPlan, TRIAL_DAYS

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new company (tenant)"""
    db = get_db()
    
    # Check if email already exists
    existing_user = await db.users.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create tenant
    tenant_data = {
        "name": request.company_name,
        "slug": request.company_name.lower().replace(" ", "-"),
        "plan": SubscriptionPlan.FREE_TRIAL,
        "status": "active",
        "trial_end": datetime.utcnow() + timedelta(days=TRIAL_DAYS),
        "subscription_status": "trial",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    tenant_result = await db.tenants.insert_one(tenant_data)
    tenant_id = tenant_result.inserted_id
    
    # Create owner user
    user_data = {
        "tenant_id": tenant_id,
        "email": request.email,
        "password_hash": hash_password(request.password),
        "role": UserRole.OWNER,
        "first_name": request.owner_name,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    user_result = await db.users.insert_one(user_data)
    user_id = user_result.inserted_id
    
    # Update tenant with owner_id
    await db.tenants.update_one(
        {"_id": tenant_id},
        {"$set": {"owner_id": user_id}}
    )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user_id), "tenant_id": str(tenant_id), "role": UserRole.OWNER}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user_id), "tenant_id": str(tenant_id)}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600,
    }


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user"""
    db = get_db()
    
    # Find user
    user = await db.users.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={
            "sub": str(user["_id"]),
            "tenant_id": str(user["tenant_id"]),
            "role": user["role"]
        }
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user["_id"]), "tenant_id": str(user["tenant_id"])}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600,
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshTokenRequest):
    """Refresh access token"""
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    access_token = create_access_token(
        data={
            "sub": str(user["_id"]),
            "tenant_id": str(user["tenant_id"]),
            "role": user["role"]
        }
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user["_id"]), "tenant_id": str(user["tenant_id"])}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": 3600,
    }
