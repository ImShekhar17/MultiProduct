# services.py
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from serviceApp.models import Product, SubscriptionPlan, UserSubscription


class SubscriptionService:
    """
    Handles all subscription-related business logic
    """
    
    @staticmethod
    def check_existing_subscription(user, product):
        """
        Check if user has an active or trial subscription for this product
        """
        return UserSubscription.objects.filter(
            user=user,
            product=product,
            status__in=['active', 'trial']
        ).first()
    
    @staticmethod
    def calculate_end_date(start_date, duration_days):
        """
        Calculate subscription end date
        """
        return start_date + timedelta(days=duration_days)
    
    @staticmethod
    def create_trial_subscription(user, product):
        """
        Create a trial subscription for a product
        """
        if not product.trial_duration:
            raise ValueError("Product does not offer trial period")
        
        # Check if user already had a trial
        previous_trial = UserSubscription.objects.filter(
            user=user,
            product=product,
            status='trial'
        ).exists()
        
        if previous_trial:
            raise ValueError("User already used trial for this product")
        
        # Get or create trial plan
        trial_plan, _ = SubscriptionPlan.objects.get_or_create(
            product=product,
            is_trial=True,
            defaults={
                'name': f'{product.name} Trial',
                'plan_type': 'weekly',
                'duration_days': product.trial_duration,
                'price': Decimal('0.00'),
                'discount': None
            }
        )
        
        start_date = timezone.now().date()
        end_date = SubscriptionService.calculate_end_date(
            start_date, 
            product.trial_duration
        )
        
        subscription = UserSubscription.objects.create(
            user=user,
            product=product,
            plan=trial_plan,
            start_date=start_date,
            end_date=end_date,
            status='trial',
            auto_renew=False
        )
        
        return subscription
    
    @staticmethod
    @transaction.atomic
    def purchase_subscription(user, product, plan, auto_renew=False):
        """
        Main method to purchase a subscription
        Handles all business logic including:
        - Validation
        - Existing subscription handling
        - Payment processing
        - Subscription creation
        """
        
        # Check for existing active subscription
        existing = SubscriptionService.check_existing_subscription(user, product)
        
        if existing:
            if existing.status == 'trial':
                # Upgrade from trial to paid
                return SubscriptionService.upgrade_from_trial(
                    existing, plan, auto_renew
                )
            else:
                raise ValueError(
                    f"User already has an {existing.status} subscription for this product"
                )
        
        # Calculate dates
        start_date = timezone.now().date()
        end_date = SubscriptionService.calculate_end_date(
            start_date, 
            plan.duration_days
        )
        
        # TODO: Process payment here
        payment_successful = SubscriptionService.process_payment(user, plan)
        
        if not payment_successful:
            raise ValueError("Payment processing failed")
        
        # Create subscription
        subscription = UserSubscription.objects.create(
            user=user,
            product=product,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status='active',
            auto_renew=auto_renew
        )
        
        # TODO: Send confirmation email
        from .tasks import send_subscription_confirmation
        send_subscription_confirmation.delay(subscription.id)
        
        # TODO: Trigger webhooks/events
        
        return subscription
    
    @staticmethod
    @transaction.atomic
    def upgrade_from_trial(trial_subscription, new_plan, auto_renew=False):
        """
        Upgrade a trial subscription to a paid plan
        """
        if trial_subscription.status != 'trial':
            raise ValueError("Can only upgrade from trial status")
        
        # Process payment
        payment_successful = SubscriptionService.process_payment(
            trial_subscription.user, 
            new_plan
        )
        
        if not payment_successful:
            raise ValueError("Payment processing failed")
        
        # Update subscription
        start_date = timezone.now().date()
        end_date = SubscriptionService.calculate_end_date(
            start_date, 
            new_plan.duration_days
        )
        
        trial_subscription.plan = new_plan
        trial_subscription.start_date = start_date
        trial_subscription.end_date = end_date
        trial_subscription.status = 'active'
        trial_subscription.auto_renew = auto_renew
        trial_subscription.save()
        
        return trial_subscription
    
    @staticmethod
    def process_payment(user, plan):
        """
        Process payment for subscription
        Integrate with payment gateway (Stripe, PayPal, etc.)
        """
        # TODO: Implement actual payment gateway integration
        # This is a placeholder
        amount = plan.final_price
        
        # Example integration structure:
        # try:
        #     charge = stripe.Charge.create(
        #         amount=int(amount * 100),
        #         currency='usd',
        #         customer=user.stripe_customer_id,
        #         description=f'Subscription for {plan.product.name}'
        #     )
        #     return charge.paid
        # except stripe.error.CardError:
        #     return False
        
        return True  # Placeholder
    
    @staticmethod
    @transaction.atomic
    def cancel_subscription(subscription):
        """
        Cancel an active subscription
        """
        if subscription.status not in ['active', 'trial']:
            raise ValueError("Can only cancel active or trial subscriptions")
        
        subscription.status = 'cancelled'
        subscription.auto_renew = False
        subscription.save()
        
        # TODO: Process refund if applicable
        
         # Send cancellation confirmation
        from .tasks import send_cancellation_confirmation
        send_cancellation_confirmation.delay(subscription.id)
        
        # TODO: Send cancellation email
        
        return subscription
    
    @staticmethod
    @transaction.atomic
    def renew_subscription(subscription):
        """
        Renew an expired subscription or process auto-renewal
        """
        if subscription.status == 'cancelled':
            raise ValueError("Cannot renew cancelled subscription")
        
        # Process payment
        payment_successful = SubscriptionService.process_payment(
            subscription.user, 
            subscription.plan
        )
        
        if not payment_successful:
            raise ValueError("Payment processing failed")
        
        # Extend subscription
        new_start = subscription.end_date + timedelta(days=1)
        new_end = SubscriptionService.calculate_end_date(
            new_start, 
            subscription.plan.duration_days
        )
        
        subscription.start_date = new_start
        subscription.end_date = new_end
        subscription.status = 'active'
        subscription.save()
        
        return subscription
    
    @staticmethod
    def check_and_expire_subscriptions():
        """
        Background task to check and expire subscriptions
        Run this as a daily cron job or Celery task
        """
        today = timezone.now().date()
        
        expired_subscriptions = UserSubscription.objects.filter(
            end_date__lt=today,
            status__in=['active', 'trial']
        )
        
        for subscription in expired_subscriptions:
            if subscription.auto_renew and subscription.status == 'active':
                try:
                    SubscriptionService.renew_subscription(subscription)
                except Exception as e:
                    # Log error and mark as expired
                    subscription.status = 'expired'
                    subscription.save()
            else:
                subscription.status = 'expired'
                subscription.save()
