import json
from datetime import UTC, datetime

from flask import current_app

from app.extensions import db
from app.models import Plan, Subscription, UsageEvent
from app.services.stripe_service import StripeService, StripeServiceError


class BillingController:
    """Controller de billing, planos, assinaturas e limites."""

    ACTIVE_STATUSES = {'active', 'trialing'}

    @staticmethod
    def listar_planos():
        try:
            planos = Plan.query.filter_by(ativo=True).order_by(Plan.preco_mensal_centavos.asc()).all()
            return {'success': True, 'plans': [plano.to_dict() for plano in planos]}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao listar planos: {str(e)}'}

    @staticmethod
    def obter_assinatura_tenant(tenant_id):
        try:
            assinatura = Subscription.query.filter_by(tenant_id=tenant_id).first()
            return {'success': True, 'subscription': assinatura.to_dict() if assinatura else None}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao obter assinatura: {str(e)}'}

    @staticmethod
    def registrar_uso(tenant_id, event_type, quantity=1, user_id=None, metadata=None):
        try:
            usage_event = UsageEvent(
                tenant_id=tenant_id,
                user_id=user_id,
                event_type=event_type,
                quantity=max(int(quantity or 1), 1),
                metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
            )
            db.session.add(usage_event)
            db.session.commit()
            return {'success': True, 'usage_event': usage_event.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao registrar uso: {str(e)}'}

    @staticmethod
    def _resolve_default_plan():
        plano = Plan.query.filter_by(codigo='free', ativo=True).first()
        if plano:
            return plano
        return Plan.query.filter_by(ativo=True).order_by(Plan.preco_mensal_centavos.asc()).first()

    @staticmethod
    def _resolve_plan_for_tenant(tenant_id):
        assinatura = Subscription.query.filter_by(tenant_id=tenant_id).first()
        if assinatura and assinatura.status in BillingController.ACTIVE_STATUSES and assinatura.plan:
            return assinatura.plan
        return BillingController._resolve_default_plan()

    @staticmethod
    def can_create_private_playlist(tenant_id):
        from app.models import Playlist

        plano = BillingController._resolve_plan_for_tenant(tenant_id)
        if not plano:
            return {'success': False, 'message': 'Nenhum plano disponivel para o tenant'}

        limite = int(plano.limite_playlists_privadas or 0)
        total_privadas = Playlist.query.filter_by(tenant_id=tenant_id, publica=False).count()
        permitido = total_privadas < limite

        return {
            'success': permitido,
            'message': (
                'Limite de playlists privadas do plano atingido'
                if not permitido
                else 'Tenant pode criar playlist privada'
            ),
            'limit': limite,
            'used': total_privadas,
            'plan': plano.to_dict(),
        }

    @staticmethod
    def iniciar_checkout(tenant_id, customer_email, plan_code, success_url, cancel_url):
        try:
            plano = Plan.query.filter_by(codigo=plan_code, ativo=True).first()
            if not plano:
                return {'success': False, 'message': 'Plano nao encontrado'}
            if not plano.stripe_price_id:
                return {'success': False, 'message': 'Plano sem stripe_price_id configurado'}

            checkout_session = StripeService.create_checkout_session(
                customer_email=customer_email,
                stripe_price_id=plano.stripe_price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'tenant_id': str(tenant_id),
                    'plan_id': str(plano.id),
                    'plan_code': plano.codigo,
                },
            )
            return {
                'success': True,
                'checkout_url': getattr(checkout_session, 'url', None) or checkout_session.get('url'),
                'checkout_session_id': getattr(checkout_session, 'id', None) or checkout_session.get('id'),
            }
        except StripeServiceError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao iniciar checkout: {str(e)}'}

    @staticmethod
    def criar_portal_cobranca(tenant_id, return_url):
        try:
            assinatura = Subscription.query.filter_by(tenant_id=tenant_id).first()
            if not assinatura or not assinatura.stripe_customer_id:
                return {'success': False, 'message': 'Tenant sem customer Stripe associado'}

            portal_session = StripeService.create_billing_portal_session(
                customer_id=assinatura.stripe_customer_id,
                return_url=return_url,
            )
            return {
                'success': True,
                'portal_url': getattr(portal_session, 'url', None) or portal_session.get('url'),
            }
        except StripeServiceError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao abrir portal: {str(e)}'}

    @staticmethod
    def _ensure_subscription(tenant_id):
        assinatura = Subscription.query.filter_by(tenant_id=tenant_id).first()
        if assinatura:
            return assinatura

        plano_default = BillingController._resolve_default_plan()
        if not plano_default:
            raise ValueError('Nao existe plano default para criar assinatura')

        assinatura = Subscription(
            tenant_id=tenant_id,
            plan_id=plano_default.id,
            status='inactive',
        )
        db.session.add(assinatura)
        db.session.flush()
        return assinatura

    @staticmethod
    def trocar_plano(tenant_id, customer_email, plan_code, success_url, cancel_url):
        """Troca de plano: free/local imediato ou checkout Stripe para pagos."""
        try:
            plano = Plan.query.filter_by(codigo=plan_code, ativo=True).first()
            if not plano:
                return {'success': False, 'message': 'Plano nao encontrado'}

            if current_app.config.get('TESTING'):
                assinatura = BillingController._ensure_subscription(tenant_id)
                assinatura.plan_id = plano.id
                assinatura.status = 'active'
                assinatura.cancel_at_period_end = False
                db.session.commit()
                return {
                    'success': True,
                    'mode': 'local',
                    'message': f'Plano alterado para {plano.nome} (modo teste)',
                    'subscription': assinatura.to_dict(),
                }

            if int(plano.preco_mensal_centavos or 0) == 0:
                assinatura = BillingController._ensure_subscription(tenant_id)
                assinatura.plan_id = plano.id
                assinatura.status = 'active'
                assinatura.cancel_at_period_end = False
                db.session.commit()
                return {
                    'success': True,
                    'mode': 'local',
                    'message': f'Plano alterado para {plano.nome}',
                    'subscription': assinatura.to_dict(),
                }

            stripe_configurado = bool(current_app.config.get('STRIPE_SECRET_KEY')) and bool(plano.stripe_price_id)
            if stripe_configurado:
                checkout_result = BillingController.iniciar_checkout(
                    tenant_id=tenant_id,
                    customer_email=customer_email,
                    plan_code=plan_code,
                    success_url=success_url,
                    cancel_url=cancel_url,
                )
                if checkout_result.get('success'):
                    checkout_result['mode'] = 'checkout'
                    checkout_result['message'] = f'Redirecionando para checkout do plano {plano.nome}'
                return checkout_result

            if current_app.config.get('DEBUG') or current_app.config.get('TESTING'):
                assinatura = BillingController._ensure_subscription(tenant_id)
                assinatura.plan_id = plano.id
                assinatura.status = 'active'
                assinatura.cancel_at_period_end = False
                db.session.commit()
                return {
                    'success': True,
                    'mode': 'local',
                    'message': (
                        f'Plano alterado para {plano.nome} em modo local '
                        '(sem checkout Stripe configurado)'
                    ),
                    'subscription': assinatura.to_dict(),
                }

            return {
                'success': False,
                'message': 'Plano pago requer stripe_price_id e STRIPE_SECRET_KEY configurados',
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao trocar plano: {str(e)}'}

    @staticmethod
    def _event_to_dict(event):
        if isinstance(event, dict):
            return event
        if hasattr(event, 'to_dict'):
            return event.to_dict()
        return {}

    @staticmethod
    def _resolve_plan_for_subscription_payload(payload):
        metadata = payload.get('metadata') or {}
        plan_id = metadata.get('plan_id')
        if plan_id:
            plan = db.session.get(Plan, int(plan_id))
            if plan:
                return plan

        items = (payload.get('items') or {}).get('data') or []
        if items:
            price_id = ((items[0] or {}).get('price') or {}).get('id')
            if price_id:
                plan = Plan.query.filter_by(stripe_price_id=price_id).first()
                if plan:
                    return plan

        return BillingController._resolve_default_plan()

    @staticmethod
    def _upsert_subscription_from_checkout(session_payload):
        metadata = session_payload.get('metadata') or {}
        tenant_id = metadata.get('tenant_id')
        if not tenant_id:
            raise ValueError('Webhook checkout sem tenant_id em metadata')

        tenant_id = int(tenant_id)
        plan_id = metadata.get('plan_id')
        plano = db.session.get(Plan, int(plan_id)) if plan_id else BillingController._resolve_default_plan()
        if not plano:
            raise ValueError('Plano nao encontrado para o checkout')

        assinatura = Subscription.query.filter_by(tenant_id=tenant_id).first()
        if not assinatura:
            assinatura = Subscription(tenant_id=tenant_id, plan_id=plano.id, status='active')
            db.session.add(assinatura)

        assinatura.plan_id = plano.id
        assinatura.status = 'active'
        assinatura.stripe_customer_id = session_payload.get('customer')
        assinatura.stripe_subscription_id = session_payload.get('subscription')
        assinatura.periodo_inicio = assinatura.periodo_inicio or datetime.now(UTC).replace(tzinfo=None)
        assinatura.cancel_at_period_end = False

    @staticmethod
    def _upsert_subscription_from_subscription_event(subscription_payload):
        metadata = subscription_payload.get('metadata') or {}
        tenant_id = metadata.get('tenant_id')
        stripe_subscription_id = subscription_payload.get('id')

        assinatura = None
        if stripe_subscription_id:
            assinatura = Subscription.query.filter_by(stripe_subscription_id=stripe_subscription_id).first()

        if not assinatura and tenant_id:
            assinatura = Subscription.query.filter_by(tenant_id=int(tenant_id)).first()

        if not assinatura:
            if not tenant_id:
                raise ValueError('Webhook subscription sem tenant_id e sem assinatura existente')
            assinatura = Subscription(tenant_id=int(tenant_id), plan_id=0, status='inactive')
            db.session.add(assinatura)

        plano = BillingController._resolve_plan_for_subscription_payload(subscription_payload)
        if not plano:
            raise ValueError('Nao foi possivel resolver plano para evento de assinatura')

        assinatura.plan_id = plano.id
        assinatura.status = subscription_payload.get('status') or 'inactive'
        assinatura.stripe_customer_id = subscription_payload.get('customer')
        assinatura.stripe_subscription_id = stripe_subscription_id
        assinatura.periodo_inicio = StripeService.ts_to_datetime(subscription_payload.get('current_period_start'))
        assinatura.periodo_fim = StripeService.ts_to_datetime(subscription_payload.get('current_period_end'))
        assinatura.cancel_at_period_end = bool(subscription_payload.get('cancel_at_period_end'))

    @staticmethod
    def processar_webhook(raw_payload, stripe_signature):
        try:
            event = StripeService.construct_event(raw_payload, stripe_signature)
            event_dict = BillingController._event_to_dict(event)
            event_type = event_dict.get('type')
            payload = (event_dict.get('data') or {}).get('object') or {}

            if event_type == 'checkout.session.completed':
                BillingController._upsert_subscription_from_checkout(payload)
            elif event_type in {
                'customer.subscription.created',
                'customer.subscription.updated',
                'customer.subscription.deleted',
            }:
                BillingController._upsert_subscription_from_subscription_event(payload)
            else:
                return {'success': True, 'message': f'Evento ignorado: {event_type}'}

            db.session.commit()
            return {'success': True, 'message': f'Webhook processado: {event_type}'}
        except StripeServiceError as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Erro ao processar webhook: {str(e)}'}
