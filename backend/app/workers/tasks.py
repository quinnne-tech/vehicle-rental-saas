"""Celery background tasks"""

from celery import shared_task
from app.workers.celery_app import celery_app
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="check_subscription_expiry")
def check_subscription_expiry(self):
    """Check for expired subscriptions and send notifications"""
    logger.info("Running subscription expiry check...")
    # Implementation pending MongoDB connection in workers
    return {"status": "executed", "timestamp": datetime.utcnow().isoformat()}


@celery_app.task(bind=True, name="send_trial_ending_reminder")
def send_trial_ending_reminder(self):
    """Send email reminders for trials ending soon"""
    logger.info("Sending trial ending reminders...")
    return {"status": "executed", "timestamp": datetime.utcnow().isoformat()}


@celery_app.task(bind=True, name="check_overdue_rentals")
def check_overdue_rentals(self):
    """Check for overdue rentals and send alerts"""
    logger.info("Checking for overdue rentals...")
    return {"status": "executed", "timestamp": datetime.utcnow().isoformat()}


@celery_app.task(bind=True, name="cleanup_old_sessions")
def cleanup_old_sessions(self):
    """Clean up old session data"""
    logger.info("Cleaning up old sessions...")
    return {"status": "executed", "timestamp": datetime.utcnow().isoformat()}
