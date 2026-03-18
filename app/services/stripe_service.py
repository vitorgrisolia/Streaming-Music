import json
from datetime import UTC, datetime

from flask import current_app


class StripeServiceError(Exception):
    """Erro de integracao com Stripe."""


class StripeService:
    """Wrapper simples para operacoes Stripe usadas pelo billing."""

    @staticmethod
    def _client():
        api_key = current_app.config.get('STRIPE_SECRET_KEY')
        if not api_key:
            raise StripeServiceError('STRIPE_SECRET_KEY nao configurada.')

        try:
            import stripe  # type: ignore
        except ImportError as exc:
            raise StripeServiceError('Biblioteca stripe nao instalada no ambiente.') from exc

        stripe.api_key = api_key
        return stripe

    @staticmethod
    def ts_to_datetime(unix_timestamp):
        if not unix_timestamp:
            return None
        return datetime.fromtimestamp(int(unix_timestamp), tz=UTC).replace(tzinfo=None)

    @classmethod
    def create_checkout_session(cls, customer_email, stripe_price_id, success_url, cancel_url, metadata=None):
        stripe = cls._client()
        payload = {
            'mode': 'subscription',
            'customer_email': customer_email,
            'line_items': [{'price': stripe_price_id, 'quantity': 1}],
            'success_url': success_url,
            'cancel_url': cancel_url,
            'metadata': metadata or {},
        }
        return stripe.checkout.Session.create(**payload)

    @classmethod
    def create_billing_portal_session(cls, customer_id, return_url):
        stripe = cls._client()
        return stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

    @classmethod
    def construct_event(cls, raw_payload, signature_header):
        webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
        if not webhook_secret:
            try:
                return json.loads(raw_payload)
            except json.JSONDecodeError as exc:
                raise StripeServiceError('Webhook com payload invalido.') from exc

        stripe = cls._client()
        try:
            return stripe.Webhook.construct_event(raw_payload, signature_header, webhook_secret)
        except Exception as exc:
            raise StripeServiceError('Assinatura do webhook Stripe invalida.') from exc
