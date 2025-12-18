from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import timedelta
import logging
from serviceApp.models import UserSubscription, Product, Invoice
# We import services inside tasks to avoid circular imports if needed, 
# but for simple tasks we can import them here if they don't import tasks.py back.
# However, NotificationService is used in send_subscription_expiry_reminders.

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def check_expired_subscriptions(self):
    """
    Daily task to check and expire subscriptions
    Also handles auto-renewal attempts
    """
    try:
        logger.info("Starting expired subscriptions check")
        SubscriptionService.check_and_expire_subscriptions()
        logger.info("Completed expired subscriptions check")
        return {"status": "success", "message": "Expired subscriptions processed"}
    except Exception as exc:
        logger.error(f"Error checking expired subscriptions: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)  # Retry after 5 minutes


@shared_task(bind=True, max_retries=3)
def send_subscription_expiry_reminder(self, subscription_id, days_before):
    """
    Send reminder email before subscription expires
    """
    try:
        subscription = UserSubscription.objects.select_related(
            'user', 'product', 'plan'
        ).get(id=subscription_id)
        
        subject = f"Your {subscription.product.name} subscription expires in {days_before} days"
        message = f"""
        Hi {subscription.user.get_full_name() or subscription.user.username},
        
        Your subscription for {subscription.product.name} ({subscription.plan.name}) 
        will expire on {subscription.end_date.strftime('%B %d, %Y')}.
        
        {'Your subscription will automatically renew.' if subscription.auto_renew else 
         'To continue using our services, please renew your subscription.'}
        
        Best regards,
        The Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [subscription.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Sent expiry reminder for subscription {subscription_id}")
        return {"status": "success", "subscription_id": subscription_id}
        
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription {subscription_id} not found")
        return {"status": "error", "message": "Subscription not found"}
    except Exception as exc:
        logger.error(f"Error sending reminder for subscription {subscription_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def check_subscriptions_expiring_soon():
    """
    Check for subscriptions expiring in 7, 3, and 1 days
    Send reminder emails
    """
    today = timezone.now().date()
    reminder_days = [7, 3, 1]
    
    for days in reminder_days:
        target_date = today + timedelta(days=days)
        
        subscriptions = UserSubscription.objects.filter(
            end_date=target_date,
            status__in=['active', 'trial']
        ).select_related('user', 'product')
        
        for subscription in subscriptions:
            send_subscription_expiry_reminder.delay(subscription.id, days)
    
    logger.info(f"Scheduled {subscriptions.count()} expiry reminders")
    return {"status": "success", "reminders_sent": subscriptions.count()}


@shared_task(bind=True, max_retries=3)
def process_failed_renewal(self, subscription_id):
    """
    Handle failed auto-renewal attempts
    Send notification and retry payment
    """
    try:
        subscription = UserSubscription.objects.select_related(
            'user', 'product', 'plan'
        ).get(id=subscription_id)
        
        if subscription.status != 'expired':
            return {"status": "skipped", "message": "Subscription not expired"}
        
        # Attempt renewal one more time
        try:
            SubscriptionService.renew_subscription(subscription)
            
            # Send success email
            send_mail(
                f"Your {subscription.product.name} subscription has been renewed",
                f"Your payment was successful and your subscription is now active.",
                settings.DEFAULT_FROM_EMAIL,
                [subscription.user.email],
                fail_silently=False,
            )
            
            return {"status": "success", "subscription_id": subscription_id}
            
        except Exception as e:
            # Send failure notification
            send_mail(
                f"Failed to renew your {subscription.product.name} subscription",
                f"""
                We were unable to process your payment for subscription renewal.
                
                Reason: {str(e)}
                
                Please update your payment method and renew manually.
                """,
                settings.DEFAULT_FROM_EMAIL,
                [subscription.user.email],
                fail_silently=False,
            )
            
            logger.error(f"Failed renewal attempt for subscription {subscription_id}: {str(e)}")
            return {"status": "failed", "subscription_id": subscription_id, "error": str(e)}
            
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription {subscription_id} not found")
        return {"status": "error", "message": "Subscription not found"}
    except Exception as exc:
        logger.error(f"Error processing failed renewal {subscription_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)


@shared_task
def generate_subscription_analytics():
    """
    Generate daily analytics report
    Track MRR, churn rate, active subscriptions, etc.
    """
    today = timezone.now().date()
    
    # Active subscriptions
    active_subs = UserSubscription.objects.filter(status='active').count()
    trial_subs = UserSubscription.objects.filter(status='trial').count()
    
    # New subscriptions today
    new_subs_today = UserSubscription.objects.filter(
        created_at__date=today,
        status='active'
    ).count()
    
    # Expired/Cancelled today
    churned_today = UserSubscription.objects.filter(
        updated_at__date=today,
        status__in=['expired', 'cancelled']
    ).count()
    
    # Calculate MRR (Monthly Recurring Revenue)
    from django.db.models import Sum, F, DecimalField
    from django.db.models.functions import Coalesce
    
    monthly_revenue = UserSubscription.objects.filter(
        status='active'
    ).annotate(
        monthly_price=F('plan__price') * (30.0 / F('plan__duration_days'))
    ).aggregate(
        mrr=Coalesce(Sum('monthly_price'), 0, output_field=DecimalField())
    )['mrr']
    
    analytics_data = {
        'date': today.isoformat(),
        'active_subscriptions': active_subs,
        'trial_subscriptions': trial_subs,
        'new_subscriptions': new_subs_today,
        'churned_subscriptions': churned_today,
        'mrr': float(monthly_revenue),
        'churn_rate': (churned_today / active_subs * 100) if active_subs > 0 else 0
    }
    
    logger.info(f"Daily analytics: {analytics_data}")
    
    # TODO: Store analytics in a metrics table or send to analytics service
    # SubscriptionMetrics.objects.create(**analytics_data)
    
    return analytics_data


@shared_task(bind=True, max_retries=2)
def send_subscription_confirmation(self, subscription_id):
    """
    Send confirmation email after successful subscription purchase
    """
    try:
        subscription = UserSubscription.objects.select_related(
            'user', 'product', 'plan'
        ).get(id=subscription_id)
        
        subject = f"Welcome to {subscription.product.name}!"
        message = f"""
        Hi {subscription.user.get_full_name() or subscription.user.username},
        
        Thank you for subscribing to {subscription.product.name}!
        
        Subscription Details:
        - Plan: {subscription.plan.name}
        - Start Date: {subscription.start_date.strftime('%B %d, %Y')}
        - End Date: {subscription.end_date.strftime('%B %d, %Y')}
        - Status: {subscription.get_status_display()}
        - Auto-Renew: {'Yes' if subscription.auto_renew else 'No'}
        
        You can manage your subscription anytime from your account dashboard.
        
        Welcome aboard!
        The Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [subscription.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Sent confirmation email for subscription {subscription_id}")
        return {"status": "success", "subscription_id": subscription_id}
        
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription {subscription_id} not found")
        return {"status": "error", "message": "Subscription not found"}
    except Exception as exc:
        logger.error(f"Error sending confirmation for subscription {subscription_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=2)
def send_cancellation_confirmation(self, subscription_id):
    """
    Send confirmation email after subscription cancellation
    """
    try:
        subscription = UserSubscription.objects.select_related(
            'user', 'product', 'plan'
        ).get(id=subscription_id)
        
        subject = f"Your {subscription.product.name} subscription has been cancelled"
        message = f"""
        Hi {subscription.user.get_full_name() or subscription.user.username},
        
        We're sorry to see you go. Your subscription to {subscription.product.name} has been cancelled.
        
        You will continue to have access until: {subscription.end_date.strftime('%B %d, %Y')}
        
        If you change your mind, you can reactivate your subscription anytime.
        
        We'd love to hear your feedback on why you cancelled.
        
        Best regards,
        The Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [subscription.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Sent cancellation confirmation for subscription {subscription_id}")
        return {"status": "success", "subscription_id": subscription_id}
        
    except UserSubscription.DoesNotExist:
        logger.error(f"Subscription {subscription_id} not found")
        return {"status": "error", "message": "Subscription not found"}
    except Exception as exc:
        logger.error(f"Error sending cancellation confirmation for subscription {subscription_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_old_expired_subscriptions():
    """
    Archive or cleanup expired subscriptions older than 1 year
    Run monthly
    """
    one_year_ago = timezone.now().date() - timedelta(days=365)
    
    old_subscriptions = UserSubscription.objects.filter(
        status__in=['expired', 'cancelled'],
        updated_at__date__lt=one_year_ago
    )
    
    count = old_subscriptions.count()
    
    # Option 1: Archive to a separate table
    # for sub in old_subscriptions:
    #     ArchivedSubscription.objects.create_from_subscription(sub)
    
    # Option 2: Just delete (not recommended)
    # old_subscriptions.delete()
    
    logger.info(f"Found {count} old subscriptions for cleanup")
    return {"status": "success", "old_subscriptions": count}


@shared_task
def send_subscription_expiry_reminders():
    """
    Send expiry reminder notifications for subscriptions expiring in 7 days
    """
    from serviceApp.services.services import NotificationService
    reminder_date = timezone.now().date() + timedelta(days=7)
    
    expiring_subscriptions = UserSubscription.objects.filter(
        end_date=reminder_date,
        status='active'
    )
    
    for subscription in expiring_subscriptions:
        NotificationService.send_expiry_reminder_notification(subscription)
    
    return f"Sent reminders for {expiring_subscriptions.count()} subscriptions"


@shared_task(bind=True, max_retries=3)
def send_email_notification_task(self, subject, template_name, context, recipient_list):
    """
    Generic task to send emails asynchronously.
    Handles serialization of complex objects like Invoices.
    """
    try:
        # Re-fetch invoices if IDs were provided (for serialization safety)
        if 'invoice_ids' in context:
            invoice_ids = context.pop('invoice_ids')
            invoices = Invoice.objects.filter(id__in=invoice_ids)
            context['invoices'] = invoices

        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        logger.info(f"Successfully sent email: {subject} to {recipient_list}")
        return {"status": "success", "subject": subject}
        
    except Exception as exc:
        logger.error(f"Error sending email '{subject}': {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


# celery.py (Add this to your project's celery configuration)
"""
from celery import Celery
from celery.schedules import crontab

app = Celery('your_project')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat Schedule
app.conf.beat_schedule = {
    'check-expired-subscriptions': {
        'task': 'serviceApp.tasks.tasks.check_expired_subscriptions',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'check-subscriptions-expiring-soon': {
        'task': 'serviceApp.tasks.tasks.check_subscriptions_expiring_soon',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    'generate-subscription-analytics': {
        'task': 'serviceApp.tasks.tasks.generate_subscription_analytics',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
    'cleanup-old-subscriptions': {
        'task': 'serviceApp.tasks.tasks.cleanup_old_expired_subscriptions',
        'schedule': crontab(day_of_month=1, hour=2, minute=0),  # Monthly on 1st at 2 AM
    },
}

app.autodiscover_tasks()
"""