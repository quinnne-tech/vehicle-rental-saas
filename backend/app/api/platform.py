"""Platform admin API endpoints"""

from fastapi import APIRouter, HTTPException, status, Request
from typing import List
from app.core.constants import UserRole
from app.models.schemas import TenantResponse
from app.database.connection import get_db

router = APIRouter()


def verify_super_admin(request: Request):
    """Verify user is super admin"""
    if not hasattr(request.state, "user_role") or request.state.user_role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can access this endpoint"
        )


@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(request: Request):
    """List all tenants (super admin only)"""
    verify_super_admin(request)
    db = get_db()
    tenants = await db.tenants.find().to_list(None)
    
    return [
        TenantResponse(
            id=str(t["_id"]),
            name=t["name"],
            plan=t["plan"],
            status=t["status"],
            trial_end=t.get("trial_end"),
            created_at=t["created_at"]
        )
        for t in tenants
    ]


@router.get("/analytics")
async def get_global_analytics(request: Request):
    """Get global platform analytics (super admin only)"""
    verify_super_admin(request)
    db = get_db()
    
    total_tenants = await db.tenants.count_documents({})
    active_subscriptions = await db.subscriptions.count_documents({"status": "active"})
    total_users = await db.users.count_documents({})
    
    return {
        "total_tenants": total_tenants,
        "active_subscriptions": active_subscriptions,
        "total_users": total_users,
    }
