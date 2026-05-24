"""Application Constants"""

# User Roles
class UserRole:
    SUPER_ADMIN = "super_admin"
    OWNER = "owner"
    MANAGER = "manager"
    STAFF = "staff"


TENANT_ROLES = [UserRole.OWNER, UserRole.MANAGER, UserRole.STAFF]
ALL_ROLES = [UserRole.SUPER_ADMIN] + TENANT_ROLES


# Subscription Plans
class SubscriptionPlan:
    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"
    FREE_TRIAL = "free_trial"


PLAN_LIMITS = {
    SubscriptionPlan.STARTER: {"vehicles": 5, "users": 2, "storage_gb": 10},
    SubscriptionPlan.GROWTH: {"vehicles": 25, "users": 5, "storage_gb": 100},
    SubscriptionPlan.ENTERPRISE: {"vehicles": None, "users": None, "storage_gb": None},
    SubscriptionPlan.FREE_TRIAL: {"vehicles": 10, "users": 3, "storage_gb": 5},
}

PLAN_PRICES = {
    SubscriptionPlan.STARTER: 99,  # $99/month
    SubscriptionPlan.GROWTH: 299,  # $299/month
    SubscriptionPlan.ENTERPRISE: 0,  # Custom pricing
}

TRIAL_DAYS = 14


# Vehicle Status
class VehicleStatus:
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


# Rental Status
class RentalStatus:
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


# Subscription Status
class SubscriptionStatus:
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


# Transaction Type
class TransactionType:
    PAYMENT = "payment"
    REFUND = "refund"
    DEPOSIT = "deposit"
    PENALTY = "penalty"


# Notifications
class NotificationChannel:
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"


class NotificationType:
    RENTAL_CREATED = "rental_created"
    RENTAL_OVERDUE = "rental_overdue"
    PAYMENT_RECEIVED = "payment_received"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    TRIAL_ENDING = "trial_ending"
    VEHICLE_MAINTENANCE = "vehicle_maintenance"
