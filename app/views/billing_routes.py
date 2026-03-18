from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.controllers.billing_controller import BillingController

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')


@billing_bp.route('/planos')
@login_required
def planos():
    """Tela de planos e assinatura atual do tenant."""
    planos_resultado = BillingController.listar_planos()
    assinatura_resultado = BillingController.obter_assinatura_tenant(current_user.tenant_id)

    planos = planos_resultado.get('plans', []) if planos_resultado.get('success') else []
    assinatura = assinatura_resultado.get('subscription') if assinatura_resultado.get('success') else None

    if not planos_resultado.get('success'):
        flash(planos_resultado.get('message', 'Erro ao carregar planos'), 'error')
    if not assinatura_resultado.get('success'):
        flash(assinatura_resultado.get('message', 'Erro ao carregar assinatura'), 'error')

    assinatura_plan_id = assinatura.get('plan_id') if assinatura else None
    assinatura_status = assinatura.get('status') if assinatura else 'inactive'

    return render_template(
        'billing_planos.html',
        planos=planos,
        assinatura=assinatura,
        assinatura_plan_id=assinatura_plan_id,
        assinatura_status=assinatura_status,
    )


@billing_bp.route('/planos/trocar', methods=['POST'])
@login_required
def trocar_plano():
    """Processa troca de plano a partir da tela de billing."""
    plan_code = (request.form.get('plan_code') or '').strip().lower()
    if not plan_code:
        flash('Plano nao informado para troca.', 'error')
        return redirect(url_for('billing.planos'))

    success_url = url_for('billing.planos', _external=True)
    cancel_url = url_for('billing.planos', _external=True)
    resultado = BillingController.trocar_plano(
        tenant_id=current_user.tenant_id,
        customer_email=current_user.email,
        plan_code=plan_code,
        success_url=success_url,
        cancel_url=cancel_url,
    )

    if not resultado.get('success'):
        flash(resultado.get('message', 'Nao foi possivel trocar de plano'), 'error')
        return redirect(url_for('billing.planos'))

    if resultado.get('mode') == 'checkout' and resultado.get('checkout_url'):
        flash(resultado.get('message', 'Redirecionando para checkout...'), 'info')
        return redirect(resultado['checkout_url'])

    flash(resultado.get('message', 'Plano atualizado com sucesso'), 'success')
    return redirect(url_for('billing.planos'))
