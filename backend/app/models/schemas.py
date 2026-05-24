"""Pydantic request/response schemas"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Auth Schemas
class RegisterRequest(BaseModel):
    """Company registration request"""
    company_name: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    owner_name: str


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


# Tenant Schemas
class TenantResponse(BaseModel):
    """Tenant response"""
    id: str = Field(..., alias="_id")
    name: str
    plan: str
    status: str
    trial_end: Optional[datetime] = None
    created_at: datetime

    class Config:
        populate_by_name = True


# Vehicle Schemas
class VehicleCreate(BaseModel):
    """Create vehicle request"""
    brand: str
    model: str
    year: int
    license_plate: str
    daily_rate: float
    description: Optional[str] = None


class VehicleResponse(BaseModel):
    """Vehicle response"""
    id: str = Field(..., alias="_id")
    brand: str
    model: str
    year: int
    license_plate: str
    status: str
    daily_rate: float
    created_at: datetime

    class Config:
        populate_by_name = True


# Renter Schemas
class RenterCreate(BaseModel):
    """Create renter request"""
    name: str
    email: EmailStr
    phone: str
    id_number: str
    address: Optional[str] = None


class RenterResponse(BaseModel):
    """Renter response"""
    id: str = Field(..., alias="_id")
    name: str
    email: str
    phone: str
    created_at: datetime

    class Config:
        populate_by_name = True


# Rental Schemas
class RentalCreate(BaseModel):
    """Create rental request"""
    vehicle_id: str
    renter_id: str
    start_date: datetime
    end_date: datetime
    notes: Optional[str] = None


class RentalResponse(BaseModel):
    """Rental response"""
    id: str = Field(..., alias="_id")
    vehicle_id: str
    renter_id: str
    start_date: datetime
    end_date: datetime
    status: str
    total_cost: float
    created_at: datetime

    class Config:
        populate_by_name = True


# Subscription Schemas
class PlanResponse(BaseModel):
    """Subscription plan response"""
    id: str
    name: str
    price: float
    vehicles_limit: Optional[int] = None
    users_limit: Optional[int] = None
    storage_limit: Optional[int] = None


class SubscriptionResponse(BaseModel):
    """Subscription response"""
    plan: str
    status: str
    started_at: datetime
    expires_at: Optional[datetime] = None
    auto_renew: bool


# Dashboard Schemas
class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_vehicles: int
    available_vehicles: int
    active_rentals: int
    total_revenue: float
    monthly_revenue: float


class DashboardResponse(BaseModel):
    """Dashboard response"""
    stats: DashboardStats
    recent_rentals: List[RentalResponse]
    upcoming_returns: List[RentalResponse]
