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
from serviceApp.services.services import SubscriptionService


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
            'errors': serializer.errors
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
    
    def post(self, request):
        serializer = PurchaseSubscriptionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
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


