#!/usr/bin/env python3
"""
Stripe integration for donation-based premium subscriptions.
$5/month donations unlock premium features.
"""

import os
import stripe
from datetime import datetime, timedelta
from models import db, User

# Initialize Stripe with keys from environment variables
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')  # Use test key by default
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_...')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Price ID for $5/month subscription (create this in Stripe Dashboard)
MONTHLY_PRICE_ID = os.getenv('STRIPE_MONTHLY_PRICE_ID', 'price_...')


class StripeService:
    """Service class for handling Stripe operations."""
    
    @staticmethod
    def create_customer(user):
        """Create a Stripe customer for a user."""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.username,
                metadata={'user_id': user.id}
            )
            
            # Save customer ID to user record
            user.stripe_customer_id = customer.id
            db.session.commit()
            
            return customer
            
        except stripe.error.StripeError as e:
            print(f"Stripe customer creation failed: {e}")
            return None
    
    @staticmethod
    def create_checkout_session(user, success_url, cancel_url):
        """Create a Stripe Checkout session for subscription."""
        try:
            # Create customer if doesn't exist
            if not user.stripe_customer_id:
                customer = StripeService.create_customer(user)
                if not customer:
                    return None
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=user.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': MONTHLY_PRICE_ID,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                allow_promotion_codes=True,
                billing_address_collection='auto',
                customer_update={'address': 'auto', 'name': 'auto'}
            )
            
            return checkout_session
            
        except stripe.error.StripeError as e:
            print(f"Stripe checkout session creation failed: {e}")
            return None
    
    @staticmethod
    def create_billing_portal_session(user, return_url):
        """Create a billing portal session for subscription management."""
        try:
            print(f"🏗️ Creating billing portal for customer: {user.stripe_customer_id}")
            
            if not user.stripe_customer_id:
                print("❌ No stripe_customer_id provided")
                return None
            
            # Check current Stripe API key
            api_key = stripe.api_key
            print(f"🔑 Using Stripe API key: {api_key[0:7]}...{api_key[-4:] if api_key else 'None'}")
            
            portal_session = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url=return_url,
            )
            
            print(f"✅ Portal session created successfully: {portal_session.id}")
            return portal_session
            
        except stripe.error.StripeError as e:
            print(f"❌ Stripe billing portal creation failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error code: {getattr(e, 'code', 'N/A')}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error creating billing portal: {e}")
            return None
    
    @staticmethod
    def handle_subscription_created(subscription):
        """Handle successful subscription creation."""
        try:
            customer_id = subscription['customer']
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            
            if user:
                user.subscription_id = subscription['id']
                user.subscription_status = 'active'
                user.subscription_start = datetime.utcnow()
                user.last_payment = datetime.utcnow()
                
                # Set subscription end based on current period
                if subscription.get('current_period_end'):
                    user.subscription_end = datetime.fromtimestamp(
                        subscription['current_period_end']
                    )
                
                db.session.commit()
                print(f"✅ User {user.username} subscription activated")
                return True
                
        except Exception as e:
            print(f"❌ Error handling subscription created: {e}")
            return False
    
    @staticmethod
    def handle_subscription_updated(subscription):
        """Handle subscription updates (renewals, changes)."""
        try:
            customer_id = subscription['customer']
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            
            if user:
                user.subscription_status = subscription['status']
                
                if subscription.get('current_period_end'):
                    user.subscription_end = datetime.fromtimestamp(
                        subscription['current_period_end']
                    )
                
                # Update last payment if status is active
                if subscription['status'] == 'active':
                    user.last_payment = datetime.utcnow()
                
                db.session.commit()
                print(f"✅ User {user.username} subscription updated to {subscription['status']}")
                
        except Exception as e:
            print(f"❌ Error handling subscription updated: {e}")
    
    @staticmethod
    def handle_subscription_deleted(subscription):
        """Handle subscription cancellation."""
        try:
            customer_id = subscription['customer']
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            
            if user:
                user.subscription_status = 'canceled'
                user.subscription_end = datetime.utcnow()
                
                db.session.commit()
                print(f"✅ User {user.username} subscription canceled")
                
        except Exception as e:
            print(f"❌ Error handling subscription deleted: {e}")
    
    @staticmethod
    def handle_invoice_payment_succeeded(invoice):
        """Handle successful payment."""
        try:
            customer_id = invoice['customer']
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            
            if user:
                user.last_payment = datetime.utcnow()
                user.subscription_status = 'active'
                
                db.session.commit()
                print(f"✅ Payment succeeded for user {user.username}")
                
        except Exception as e:
            print(f"❌ Error handling payment succeeded: {e}")
    
    @staticmethod
    def handle_invoice_payment_failed(invoice):
        """Handle failed payment."""
        try:
            customer_id = invoice['customer']
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            
            if user:
                user.subscription_status = 'past_due'
                db.session.commit()
                print(f"⚠️ Payment failed for user {user.username}")
                
        except Exception as e:
            print(f"❌ Error handling payment failed: {e}")


def get_stripe_public_key():
    """Get the Stripe publishable key for frontend."""
    return STRIPE_PUBLISHABLE_KEY