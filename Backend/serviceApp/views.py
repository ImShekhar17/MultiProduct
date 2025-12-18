from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required,login_not_required
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from serviceApp.services.services import SubscriptionService,InvoiceService,PaymentService,NotificationService


from serviceApp.models import *
from serviceApp.serializers import *

User = get_user_model()

logger = logging.getLogger(__name__)

# Create your views here.

class ProductListAPIView(APIView):
    """
    List all active products with their plans
    """
    def get(self, request):
        products = Product.objects.filter(
            is_active=True
        ).prefetch_related(
            Prefetch('plans', queryset=SubscriptionPlan.objects.filter(is_trial=False))
        )
        
        serializer = ProductSerializer(products, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    """
    Get details of a specific product
    """
    def get(self, request, product_id):
        try:
            product = Product.objects.prefetch_related('plans').get(
                id=product_id, 
                is_active=True
            )
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class SubscriptionListAPIView(APIView):
    """
    List all subscriptions for the authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        subscriptions = SubscriptionPlan.objects.filter(
            user=request.user
        ).select_related('product').order_by('-created_at')
        
        serializer = SubscriptionPlanSerializer(subscriptions, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class UserSubscriptionListAPIView(APIView):
    """
    List all subscriptions for the authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        subscriptions = UserSubscription.objects.filter(
            user=request.user
        ).select_related('product', 'plan').order_by('-created_at')
        
        serializer = UserSubscriptionSerializer(subscriptions, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class StartTrialAPIView(APIView):
    """
    Start a trial subscription for a product
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({
                'success': False,
                'error': 'Product ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Product not found or inactive'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            subscription = SubscriptionService.create_trial_subscription(
                request.user, 
                product
            )
            
            serializer = UserSubscriptionSerializer(subscription)
            return Response({
                'success': True,
                'message': 'Trial started successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PurchaseSubscriptionAPIView(APIView):
    """
    Purchase a subscription plan
    """
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        #!TODO to get user per user product user request.user for user product
        purchase_product = SubscriptionPlan.objects.filter(is_trial=False).select_related('product')
        serializer = SubscriptionPlanSerializer(purchase_product,many=True)
        
        return Response({
            'success': True,
            "data": serializer.data,
            'message': 'your purchase a subscription for product'
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = PurchaseSubscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        try:
            subscription = SubscriptionService.purchase_subscription(
                user=request.user,
                product=validated_data['product'],
                plan=validated_data['plan'],
                auto_renew=validated_data.get('auto_renew', False)
            )
            
            response_serializer = UserSubscriptionSerializer(subscription)
            return Response({
                'success': True,
                'message': 'Subscription purchased successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CancelSubscriptionAPIView(APIView):
    """
    Cancel an active subscription
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, subscription_id):
        try:
            subscription = UserSubscription.objects.get(
                id=subscription_id,
                user=request.user
            )
        except UserSubscription.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Subscription not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            subscription = SubscriptionService.cancel_subscription(subscription)
            
            serializer = UserSubscriptionSerializer(subscription)
            return Response({
                'success': True,
                'message': 'Subscription cancelled successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class RenewSubscriptionAPIView(APIView):
    """
    Manually renew a subscription
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, subscription_id):
        try:
            subscription = UserSubscription.objects.get(
                id=subscription_id,
                user=request.user
            )
        except UserSubscription.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Subscription not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            subscription = SubscriptionService.renew_subscription(subscription)
            
            serializer = UserSubscriptionSerializer(subscription)
            return Response({
                'success': True,
                'message': 'Subscription renewed successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# #!TODO To put all api in one api

# class SubscriptionAPIView(APIView):
#     """
#     Unified subscription management endpoint
#     Actions: get_plans, purchase, cancel, renew
#     """
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         """Get available subscription plans"""
#         purchase_product = SubscriptionPlan.objects.filter(is_trial=False).select_related('product')
#         serializer = SubscriptionPlanSerializer(purchase_product, many=True)
        
#         return Response({
#             'success': True,
#             'data': serializer.data,
#             'message': 'Available subscription plans'
#         }, status=status.HTTP_200_OK)
    
#     def post(self, request, subscription_id=None):
#         """
#         Handle subscription actions based on 'action' parameter
#         - purchase: Create new subscription
#         - cancel: Cancel active subscription
#         - renew: Manually renew subscription
#         """
#         action = request.data.get('action')
        
#         if not action:
#             return Response({
#                 'success': False,
#                 'error': "Action parameter required: 'purchase', 'cancel', or 'renew'"
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         action_map = {
#             'purchase': self._handle_purchase,
#             'cancel': self._handle_cancel,
#             'renew': self._handle_renew,
#         }
        
#         handler = action_map.get(action)
#         if not handler:
#             return Response({
#                 'success': False,
#                 'error': f"Unknown action: {action}"
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         return handler(request, subscription_id)
    
#     def _handle_purchase(self, request, subscription_id):
#         """Handle subscription purchase"""
#         serializer = PurchaseSubscriptionSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response({
#                 'success': False,
#                 'errors': serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         validated_data = serializer.validated_data
        
#         try:
#             subscription = SubscriptionService.purchase_subscription(
#                 user=request.user,
#                 product=validated_data['product'],
#                 plan=validated_data['plan'],
#                 auto_renew=validated_data.get('auto_renew', False)
#             )
            
#             response_serializer = UserSubscriptionSerializer(subscription)
#             return Response({
#                 'success': True,
#                 'message': 'Subscription purchased successfully',
#                 'data': response_serializer.data
#             }, status=status.HTTP_201_CREATED)
            
#         except ValueError as e:
#             return Response({
#                 'success': False,
#                 'error': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)
    
#     def _handle_cancel(self, request, subscription_id):
#         """Handle subscription cancellation"""
#         if not subscription_id:
#             return Response({
#                 'success': False,
#                 'error': 'subscription_id required for cancel action'
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             subscription = UserSubscription.objects.get(
#                 id=subscription_id,
#                 user=request.user
#             )
#         except UserSubscription.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'error': 'Subscription not found'
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         try:
#             subscription = SubscriptionService.cancel_subscription(subscription)
            
#             serializer = UserSubscriptionSerializer(subscription)
#             return Response({
#                 'success': True,
#                 'message': 'Subscription cancelled successfully',
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK)
            
#         except ValueError as e:
#             return Response({
#                 'success': False,
#                 'error': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)
    
#     def _handle_renew(self, request, subscription_id):
#         """Handle subscription renewal"""
#         if not subscription_id:
#             return Response({
#                 'success': False,
#                 'error': 'subscription_id required for renew action'
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             subscription = UserSubscription.objects.get(
#                 id=subscription_id,
#                 user=request.user
#             )
#         except UserSubscription.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'error': 'Subscription not found'
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         try:
#             subscription = SubscriptionService.renew_subscription(subscription)
            
#             serializer = UserSubscriptionSerializer(subscription)
#             return Response({
#                 'success': True,
#                 'message': 'Subscription renewed successfully',
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK)
            
#         except ValueError as e:
#             return Response({
#                 'success': False,
#                 'error': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)


#!TODO: Add Invoice/Payment related views

class CreateInvoiceAPIView(APIView):
    """
    Create invoice for subscription purchase or renewal
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        subscription_id = request.data.get('subscription_id')
        amount = request.data.get('amount')
        invoice_type = request.data.get('type', 'purchase')  # 'purchase' or 'renewal'
        
        try:
            user_subscription = UserSubscription.objects.get(
                id=subscription_id,
                user=request.user
            )
        except UserSubscription.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Subscription not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Create invoice
            invoice = InvoiceService.create_invoice(user_subscription, amount)
            
            # Send appropriate notification
            if invoice_type == 'renewal':
                NotificationService.send_renewal_notification(user_subscription, invoice)
            else:
                NotificationService.send_purchase_notification(user_subscription, invoice)
            
            serializer = InvoiceSerializer(invoice)
            return Response({
                'success': True,
                'message': f'{invoice_type.capitalize()} invoice created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ProcessPaymentAPIView(APIView):
    """
    Process payment for invoices
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        invoice_ids = request.data.get('invoice_ids', [])
        payment_method = request.data.get('payment_method', 'card')
        
        if not invoice_ids:
            return Response({
                'success': False,
                'error': 'No invoices provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            invoices = Invoice.objects.filter(
                id__in=invoice_ids,
                user_subscription__user=request.user,
                is_paid=False
            )
            
            if not invoices.exists():
                return Response({
                    'success': False,
                    'error': 'No valid invoices found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Process payment
            transaction = PaymentService.process_payment(
                user=request.user,
                invoices=list(invoices),
                payment_method=payment_method
            )
            
            if transaction:
                # Send payment confirmation
                NotificationService.send_payment_confirmation(request.user, transaction)
                
                serializer = TransactionSerializer(transaction)
                return Response({
                    'success': True,
                    'message': 'Payment processed successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Payment processing failed'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class GetInvoicesAPIView(APIView):
    """
    Get all invoices for authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        invoices = Invoice.objects.filter(
            user_subscription__user=request.user
        ).select_related('user_subscription__product', 'user_subscription__plan')
        
        serializer = InvoiceSerializer(invoices, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class GetNotificationsAPIView(APIView):
    """
    Get all notifications for authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        notifications = Notification.objects.filter(
            receiver=request.user
        ).order_by('-created_at')
        
        unread_count = notifications.filter(is_read=False).count()
        
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response({
            'success': True,
            'unread_count': unread_count,
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class MarkNotificationAsReadAPIView(APIView):
    """
    Mark notification as read
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                receiver=request.user
            )
        except Notification.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Notification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        notification.is_read = True
        notification.save()
        
        serializer = NotificationSerializer(notification)
        return Response({
            'success': True,
            'message': 'Notification marked as read',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


# tasks.py (For Celery - Send expiry reminders periodically)



