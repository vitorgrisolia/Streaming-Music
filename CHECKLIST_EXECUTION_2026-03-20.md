# Execução do Checklist SaaS (2026-03-20)

## 1) Configurar `.env` com valores reais (`STRIPE_*`, `SMTP_*`, `APP_BASE_URL`)

Status: **PARCIAL / PENDENTE**

Resultado da validação:

- `APP_BASE_URL`: **OK** (`http://localhost:5000`)
- `STRIPE_SECRET_KEY`: **PENDENTE** (placeholder)
- `STRIPE_WEBHOOK_SECRET`: **PENDENTE** (placeholder)
- `SMTP_HOST`: **PENDENTE** (placeholder)
- `SMTP_USERNAME`: **PENDENTE** (placeholder)
- `SMTP_PASSWORD`: **PENDENTE** (placeholder)

Conclusão:

- Estrutura do `.env` está pronta.
- Faltam credenciais reais de Stripe e SMTP.

## 2) Subir staging e rodar `flask --app run.py db upgrade`

Status: **OK (simulação local em modo production)**

Comando executado:

```powershell
$env:FLASK_ENV='production'; flask --app run.py db upgrade; Remove-Item Env:FLASK_ENV
```

Resultado:

- Migrações executadas sem erro no perfil de produção.

## 3) Validar fluxo completo (cadastro → verificação de e-mail → login → upgrade → webhook → assinatura ativa)

Status: **OK**

Coberto por teste automatizado:

- `test_fluxo_completo_cadastro_verificacao_login_upgrade_webhook`

Resultado:

- Fluxo completo passou.

## 4) Testar falhas críticas (webhook inválido, token expirado, downgrade para free)

Status: **OK**

Coberto por testes automatizados:

- `test_webhook_invalido_retorna_erro_controlado`
- `test_reset_token_expirado_bloqueia_redefinicao`
- `test_downgrade_para_free_funciona`

Resultado:

- Todos passaram com comportamento esperado.

## 5) Liberar para 3-5 usuários piloto e medir conversão/erros/suporte

Status: **BLOQUEADO (depende de operação externa)**

Motivo:

- Exige ambiente de staging público + usuários reais + janela de observação.

Pré-requisitos já prontos no sistema:

- tracking de eventos de uso (`usage_events`)
- logs de auditoria (`audit_logs`)
- fluxo de troca de plano e assinatura por tenant
- webhook Stripe implementado

## Evidência de execução de testes

Comando:

```bash
python -m unittest tests/test_application.py
```

Resultado:

- `Ran 16 tests ... OK`
