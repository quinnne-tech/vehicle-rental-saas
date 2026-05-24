"""MongoDB Document Models"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid objectid {v}")
        return ObjectId(v)

    def __repr__(self):
        return f"ObjectId('{self}')'


class BaseTenantModel(BaseModel):
    """Base model for tenant-scoped documents"""
    tenant_id: Optional[PyObjectId] = Field(None, alias="_tenant_id")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class TenantModel(BaseModel):
    """Tenant document model"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    name: str
    slug: str
    plan: str = "free_trial"
    status: str = "active"
    owner_id: Optional[PyObjectId] = None
    trial_end: Optional[datetime] = None
    subscription_status: str = "trial"
    logo_url: Optional[str] = None
    accent_color: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserModel(BaseTenantModel):
    """User document model"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    email: str
    password_hash: str
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class VehicleModel(BaseTenantModel):
    """Vehicle document model"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    brand: str
    model: str
    year: int
    license_plate: str
    status: str = "available"
    daily_rate: float
    mileage: int = 0
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class RenterModel(BaseTenantModel):
    """Renter document model"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    name: str
    email: str
    phone: str
    id_number: str
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class RentalModel(BaseTenantModel):
    """Rental document model"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    vehicle_id: PyObjectId
    renter_id: PyObjectId
    start_date: datetime
    end_date: datetime
    status: str = "active"
    daily_rate: float
    total_cost: float = 0.0
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class TransactionModel(BaseTenantModel):
    """Transaction document model"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    rental_id: Optional[PyObjectId] = None
    type: str
    amount: float
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
