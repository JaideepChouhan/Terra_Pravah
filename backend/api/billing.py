"""
Terra Pravah - Billing API
==========================
Subscription management and Stripe integration.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.models.models import db, User, Subscription

billing_bp = Blueprint('billing', __name__)


@billing_bp.route('/plans', methods=['GET'])
def list_plans():
    """List available subscription plans."""
    plans = current_app.config.get('PLANS', {})
    
    return jsonify({
        'plans': [
            {
                'id': plan_id,
                'name': plan['name'],
                'price_monthly': plan['price_monthly'],
                'price_yearly': plan['price_yearly'],
                'max_projects': plan['max_projects'],
                'max_file_size_mb': plan['max_file_size_mb'],
                'max_team_members': plan['max_team_members'],
                'features': plan['features']
            }
            for plan_id, plan in plans.items()
        ]
    })


@billing_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_subscription():
    """Get current user's subscription details."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    plan = current_app.config['PLANS'].get(user.subscription_plan, {})
    
    # Get active subscription
    subscription = Subscription.query.filter_by(
        user_id=user_id,
        status='active'
    ).first()
    
    return jsonify({
        'subscription': {
            'plan': user.subscription_plan,
            'plan_name': plan.get('name', user.subscription_plan),
            'status': user.subscription_status,
            'features': plan.get('features', []),
            'limits': {
                'max_projects': plan.get('max_projects', 3),
                'max_file_size_mb': plan.get('max_file_size_mb', 100),
                'max_team_members': plan.get('max_team_members', 1)
            },
            'billing_cycle': subscription.billing_cycle if subscription else None,
            'current_period_end': subscription.current_period_end.isoformat() if subscription and subscription.current_period_end else None
        }
    })


@billing_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    """Subscribe to a plan."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    plan_id = data.get('plan')
    billing_cycle = data.get('billing_cycle', 'monthly')  # monthly or yearly
    
    if plan_id not in current_app.config.get('PLANS', {}):
        return jsonify({'error': 'Invalid plan'}), 400
    
    if plan_id == 'free':
        # Downgrade to free
        user.subscription_plan = 'free'
        user.subscription_status = 'active'
        db.session.commit()
        
        return jsonify({
            'message': 'Switched to free plan',
            'subscription': {
                'plan': 'free',
                'status': 'active'
            }
        })
    
    # For paid plans, create Stripe checkout session
    # This is a placeholder - implement actual Stripe integration
    
    stripe_key = current_app.config.get('STRIPE_SECRET_KEY')
    
    if not stripe_key:
        return jsonify({
            'error': 'Payment processing not configured',
            'message': 'Contact support to upgrade your plan'
        }), 503
    
    try:
        # Placeholder for Stripe checkout
        # In production:
        # import stripe
        # stripe.api_key = stripe_key
        # session = stripe.checkout.Session.create(...)
        
        return jsonify({
            'message': 'Checkout session created',
            'checkout_url': f'/checkout?plan={plan_id}&cycle={billing_cycle}',
            'session_id': 'placeholder_session_id'
        })
        
    except Exception as e:
        current_app.logger.error(f"Stripe error: {e}")
        return jsonify({'error': 'Payment processing failed'}), 500


@billing_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel current subscription."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.subscription_plan == 'free':
        return jsonify({'error': 'No active subscription to cancel'}), 400
    
    # Cancel in Stripe (placeholder)
    # In production, cancel via Stripe API
    
    user.subscription_status = 'cancelled'
    
    # Update subscription record
    subscription = Subscription.query.filter_by(
        user_id=user_id,
        status='active'
    ).first()
    
    if subscription:
        subscription.status = 'cancelled'
        subscription.cancelled_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Subscription cancelled. You will retain access until the end of your billing period.'
    })


@billing_bp.route('/invoices', methods=['GET'])
@jwt_required()
def list_invoices():
    """List billing invoices."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Placeholder - fetch from Stripe in production
    invoices = []
    
    return jsonify({
        'invoices': invoices
    })


@billing_bp.route('/payment-methods', methods=['GET'])
@jwt_required()
def list_payment_methods():
    """List saved payment methods."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Placeholder - fetch from Stripe in production
    payment_methods = []
    
    return jsonify({
        'payment_methods': payment_methods
    })


@billing_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks."""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    
    if not webhook_secret:
        return jsonify({'error': 'Webhook not configured'}), 500
    
    try:
        # Verify webhook signature
        # In production:
        # import stripe
        # event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        
        event_type = request.json.get('type')
        event_data = request.json.get('data', {}).get('object', {})
        
        # Handle different event types
        if event_type == 'checkout.session.completed':
            handle_checkout_completed(event_data)
        elif event_type == 'invoice.payment_succeeded':
            handle_payment_succeeded(event_data)
        elif event_type == 'invoice.payment_failed':
            handle_payment_failed(event_data)
        elif event_type == 'customer.subscription.deleted':
            handle_subscription_deleted(event_data)
        
        return jsonify({'received': True})
        
    except Exception as e:
        current_app.logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400


def handle_checkout_completed(data):
    """Handle successful checkout."""
    customer_id = data.get('customer')
    subscription_id = data.get('subscription')
    
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if user:
        # Update subscription from Stripe data
        # Fetch subscription details and update user
        pass


def handle_payment_succeeded(data):
    """Handle successful payment."""
    customer_id = data.get('customer')
    
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if user:
        user.subscription_status = 'active'
        db.session.commit()


def handle_payment_failed(data):
    """Handle failed payment."""
    customer_id = data.get('customer')
    
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if user:
        user.subscription_status = 'past_due'
        db.session.commit()
        # Send notification email


def handle_subscription_deleted(data):
    """Handle subscription cancellation."""
    customer_id = data.get('customer')
    
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if user:
        user.subscription_plan = 'free'
        user.subscription_status = 'active'
        db.session.commit()
