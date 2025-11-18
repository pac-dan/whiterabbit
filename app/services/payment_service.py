import stripe
from flask import current_app
import os


class PaymentService:
    """Service for handling Stripe payments"""

    def __init__(self):
        """Initialize Stripe client"""
        api_key = current_app.config.get('STRIPE_SECRET_KEY') or os.getenv('STRIPE_SECRET_KEY')

        if not api_key:
            raise ValueError("STRIPE_SECRET_KEY not found in configuration")

        stripe.api_key = api_key
        self.publishable_key = current_app.config.get('STRIPE_PUBLISHABLE_KEY')

    def create_payment_intent(self, amount, currency='usd', metadata=None):
        """
        Create a Stripe Payment Intent

        Args:
            amount: Amount in cents (e.g., 2000 for $20.00)
            currency: Currency code (default: 'usd')
            metadata: Optional metadata dict

        Returns:
            Payment Intent object
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount),
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )

            return intent

        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe Payment Intent Error: {str(e)}')
            raise Exception(f'Payment error: {str(e)}')

    def retrieve_payment_intent(self, payment_intent_id):
        """
        Retrieve a Payment Intent by ID

        Args:
            payment_intent_id: Stripe Payment Intent ID

        Returns:
            Payment Intent object
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent

        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe Retrieve Error: {str(e)}')
            raise Exception(f'Payment retrieval error: {str(e)}')

    def confirm_payment(self, payment_intent_id):
        """
        Confirm a payment has been completed

        Args:
            payment_intent_id: Stripe Payment Intent ID

        Returns:
            True if payment succeeded, False otherwise
        """
        try:
            intent = self.retrieve_payment_intent(payment_intent_id)
            return intent.status == 'succeeded'

        except Exception as e:
            current_app.logger.error(f'Payment confirmation error: {str(e)}')
            return False

    def create_refund(self, payment_intent_id, amount=None, reason=None):
        """
        Create a refund for a payment

        Args:
            payment_intent_id: Stripe Payment Intent ID
            amount: Amount to refund in cents (None for full refund)
            reason: Reason for refund

        Returns:
            Refund object
        """
        try:
            refund_params = {
                'payment_intent': payment_intent_id
            }

            if amount:
                refund_params['amount'] = int(amount)

            if reason:
                refund_params['reason'] = reason

            refund = stripe.Refund.create(**refund_params)

            return refund

        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe Refund Error: {str(e)}')
            raise Exception(f'Refund error: {str(e)}')

    def get_payment_status(self, payment_intent_id):
        """
        Get human-readable payment status

        Args:
            payment_intent_id: Stripe Payment Intent ID

        Returns:
            Status string
        """
        try:
            intent = self.retrieve_payment_intent(payment_intent_id)

            status_map = {
                'requires_payment_method': 'Awaiting payment method',
                'requires_confirmation': 'Awaiting confirmation',
                'requires_action': 'Requires additional action',
                'processing': 'Processing',
                'requires_capture': 'Awaiting capture',
                'canceled': 'Canceled',
                'succeeded': 'Succeeded'
            }

            return status_map.get(intent.status, intent.status)

        except Exception as e:
            current_app.logger.error(f'Get status error: {str(e)}')
            return 'Unknown'

    def create_customer(self, email, name=None, metadata=None):
        """
        Create a Stripe customer

        Args:
            email: Customer email
            name: Customer name (optional)
            metadata: Optional metadata dict

        Returns:
            Customer object
        """
        try:
            customer_params = {
                'email': email,
                'metadata': metadata or {}
            }

            if name:
                customer_params['name'] = name

            customer = stripe.Customer.create(**customer_params)

            return customer

        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe Customer Creation Error: {str(e)}')
            raise Exception(f'Customer creation error: {str(e)}')

    def handle_webhook(self, payload, sig_header):
        """
        Handle Stripe webhook event

        Args:
            payload: Raw webhook payload
            sig_header: Stripe signature header

        Returns:
            Event object
        """
        webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')

        if not webhook_secret:
            raise ValueError("STRIPE_WEBHOOK_SECRET not configured")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )

            return event

        except ValueError as e:
            current_app.logger.error(f'Invalid webhook payload: {str(e)}')
            raise Exception('Invalid payload')

        except stripe.error.SignatureVerificationError as e:
            current_app.logger.error(f'Invalid webhook signature: {str(e)}')
            raise Exception('Invalid signature')
