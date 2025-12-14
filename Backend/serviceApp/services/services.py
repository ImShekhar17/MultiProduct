from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import uuid
from serviceApp.models import Invoice, Transaction, Notification,Product, SubscriptionPlan, UserSubscription



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

class InvoiceService:
    """
    Service to handle invoice creation, payment, and email notifications
    """
    
    @staticmethod
    def generate_invoice_number():
        """Generate unique invoice number"""
        return f"INV-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    @staticmethod
    def create_invoice(user_subscription, amount=None):
        """
        Create invoice for subscription purchase or renewal
        
        Args:
            user_subscription: UserSubscription instance
            amount: Optional custom amount (defaults to plan price)
        
        Returns:
            Invoice instance
        """
        if amount is None:
            amount = user_subscription.plan.price
        
        due_date = timezone.now().date() + timedelta(days=30)
        
        invoice = Invoice.objects.create(
            user_subscription=user_subscription,
            amount=amount,
            due_date=due_date,
            is_paid=False
        )
        
        return invoice
    
    @staticmethod
    def mark_invoice_paid(invoice, transaction_ref=None):
        """
        Mark invoice as paid and create transaction record
        
        Args:
            invoice: Invoice instance
            transaction_ref: Payment transaction reference
        
        Returns:
            Updated Invoice instance
        """
        invoice.is_paid = True
        invoice.transaction_ref = transaction_ref or f"TXN-{uuid.uuid4().hex[:10].upper()}"
        invoice.save()
        
        return invoice
    
    @staticmethod
    def send_invoice_email(invoice, email_type='purchase'):
        """
        Send invoice email to user
        
        Args:
            invoice: Invoice instance
            email_type: 'purchase', 'renewal', or 'reminder'
        """
        user = invoice.user_subscription.user
        product = invoice.user_subscription.product
        plan = invoice.user_subscription.plan
        
        context = {
            'user_name': user.get_full_name() or user.first_name,
            'invoice_number': invoice.id,
            'product_name': product.name,
            'plan_name': plan.name,
            'amount': invoice.amount,
            'issued_date': invoice.issued_date,
            'due_date': invoice.due_date,
            'transaction_ref': invoice.transaction_ref,
            'is_paid': invoice.is_paid,
            'email_type': email_type,
            'site_url': settings.SITE_BASE_URL,
        }
        
        if email_type == 'purchase':
            subject = f'Invoice {invoice.id} - Purchase Confirmation'
            template_name = 'emails/invoice_purchase.html'
        elif email_type == 'renewal':
            subject = f'Invoice {invoice.id} - Subscription Renewal'
            template_name = 'emails/invoice_renewal.html'
        else:  # reminder
            subject = f'Payment Reminder - Invoice {invoice.id}'
            template_name = 'emails/invoice_reminder.html'
        
        try:
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            return True
        except Exception as e:
            print(f"Error sending invoice email: {str(e)}")
            return False


class PaymentService:
    """
    Service to handle payment transactions
    """
    
    @staticmethod
    def create_transaction(user, invoices, payment_method='card', total_amount=None):
        """
        Create transaction for one or multiple invoices
        
        Args:
            user: User instance
            invoices: List of Invoice instances
            payment_method: Payment method used
            total_amount: Optional custom total (auto-calculated if None)
        
        Returns:
            Transaction instance
        """
        if total_amount is None:
            total_amount = sum(inv.amount for inv in invoices)
        
        transaction_ref = f"TXN-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        transaction = Transaction.objects.create(
            user=user,
            total_amount=total_amount,
            transaction_ref=transaction_ref,
            payment_method=payment_method,
            status='success'
        )
        
        # Mark invoices as paid
        for invoice in invoices:
            InvoiceService.mark_invoice_paid(invoice, transaction_ref)
        
        return transaction
    
    @staticmethod
    def process_payment(user, invoices, payment_method='card'):
        """
        Process payment for invoices
        
        Args:
            user: User instance
            invoices: List of Invoice instances
            payment_method: Payment method
        
        Returns:
            Transaction instance if successful, None otherwise
        """
        try:
            transaction = PaymentService.create_transaction(
                user=user,
                invoices=invoices,
                payment_method=payment_method
            )
            return transaction
        except Exception as e:
            print(f"Payment processing error: {str(e)}")
            return None


class NotificationService:
    """
    Service to handle user notifications
    """
    
    @staticmethod
    def send_purchase_notification(user_subscription, invoice):
        """
        Send notification after subscription purchase
        
        Args:
            user_subscription: UserSubscription instance
            invoice: Invoice instance
        """
        notification = Notification.objects.create(
            receiver=user_subscription.user,
            sender=None,
            title=f'Subscription Purchased - {user_subscription.product.name}',
            message=f'Your subscription to {user_subscription.product.name} ({user_subscription.plan.name}) '
                   f'has been successfully purchased. Invoice #{invoice.id} for ${invoice.amount} '
                   f'is due on {invoice.due_date}.',
            is_read=False
        )
        
        # Send email notification
        InvoiceService.send_invoice_email(invoice, email_type='purchase')
        
        return notification
    
    @staticmethod
    def send_renewal_notification(user_subscription, invoice):
        """
        Send notification for subscription renewal
        
        Args:
            user_subscription: UserSubscription instance
            invoice: Invoice instance
        """
        notification = Notification.objects.create(
            receiver=user_subscription.user,
            sender=None,
            title=f'Subscription Renewed - {user_subscription.product.name}',
            message=f'Your subscription to {user_subscription.product.name} has been successfully renewed. '
                   f'Invoice #{invoice.id} for ${invoice.amount} is due on {invoice.due_date}.',
            is_read=False
        )
        
        # Send email notification
        InvoiceService.send_invoice_email(invoice, email_type='renewal')
        
        return notification
    
    @staticmethod
    def send_expiry_reminder_notification(user_subscription):
        """
        Send reminder notification before subscription expires
        
        Args:
            user_subscription: UserSubscription instance
        """
        days_until_expiry = (user_subscription.end_date - timezone.now().date()).days
        
        notification = Notification.objects.create(
            receiver=user_subscription.user,
            sender=None,
            title=f'Subscription Expiring Soon - {user_subscription.product.name}',
            message=f'Your subscription to {user_subscription.product.name} ({user_subscription.plan.name}) '
                   f'will expire in {days_until_expiry} days on {user_subscription.end_date}. '
                   f'Please renew your subscription to avoid service interruption.',
            is_read=False
        )
        
        # Send email reminder
        context = {
            'user_name': user_subscription.user.get_full_name() or user_subscription.user.username,
            'product_name': user_subscription.product.name,
            'plan_name': user_subscription.plan.name,
            'expiry_date': user_subscription.end_date,
            'days_until_expiry': days_until_expiry,
            'site_url': settings.SITE_BASE_URL,
        }
        
        try:
            html_message = render_to_string('emails/renewal_reminder.html', context)
            plain_message = strip_tags(html_message)
            
            email = EmailMultiAlternatives(
                subject=f'Subscription Expiring Soon - {user_subscription.product.name}',
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_subscription.user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
        except Exception as e:
            print(f"Error sending renewal reminder email: {str(e)}")
        
        return notification
    
    @staticmethod
    def send_payment_confirmation(user, transaction):
        """
        Send payment confirmation email
        
        Args:
            user: User instance
            transaction: Transaction instance
        """
        invoices = transaction.invoice_set.all()
        
        context = {
            'user_name': user.get_full_name() or user.username,
            'transaction_ref': transaction.transaction_ref,
            'total_amount': transaction.total_amount,
            'payment_method': transaction.payment_method,
            'invoices': invoices,
            'transaction_date': transaction.created_at,
            'site_url': settings.SITE_BASE_URL,
        }
        
        try:
            html_message = render_to_string('emails/payment_confirmation.html', context)
            plain_message = strip_tags(html_message)
            
            email = EmailMultiAlternatives(
                subject=f'Payment Confirmation - {transaction.transaction_ref}',
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
        except Exception as e:
            print(f"Error sending payment confirmation email: {str(e)}")
