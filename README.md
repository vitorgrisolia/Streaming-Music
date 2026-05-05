# Streaming Music Platform

Aplicação web de streaming de música com Flask (MVC), interface web, API REST e suporte SaaS com multi-tenant, planos, cobrança e segurança reforçada.

## Visão Geral

O projeto inclui:

- autenticação e sessão de usuários
- verificação de e-mail e reset de senha por token
- catálogo de artistas, álbuns e músicas
- player HTML5 para reprodução de áudio
- criação e gerenciamento de playlists
- favoritos por usuário
- isolamento por tenant (multi-tenant)
- planos (`Plan`) e assinatura por tenant (`Subscription`)
- eventos de uso para controle de limite (`UsageEvent`)
- webhook Stripe para sincronizar cobrança
- auditoria de eventos sensíveis (`AuditLog`)
- suporte a API keys (`ApiKey`)
- rate limit para API e observabilidade por request

## Stack

- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate (Alembic)
- Flask-Login
- Flask-Bcrypt
- Flask-CORS
- Stripe API
- sentry-sdk (opcional)
- python-dotenv

## Estrutura do Projeto

```text
Streaming Music/
|-- app/
|   |-- __init__.py
|   |-- extensions.py
|   |-- config/
|   |   `-- settings.py
|   |-- controllers/
|   |   |-- auth_controller.py
|   |   |-- billing_controller.py
|   |   |-- music_controller.py
|   |   `-- playlist_controller.py
|   |-- models/
|   |   |-- tenant.py
|   |   |-- membership.py
|   |   |-- plan.py
|   |   |-- subscription.py
|   |   |-- usage_event.py
|   |   |-- audit_log.py
|   |   `-- api_key.py
|   |-- services/
|   |   |-- stripe_service.py
|   |   `-- email_service.py
|   |-- views/
|   |   |-- api_routes.py
|   |   |-- billing_routes.py
|   |   `-- ...
|   |-- templates/
|   |   |-- billing_planos.html
|   |   `-- ...
|   `-- static/
|-- migrations/
|   `-- versions/
|-- instance/
|-- tests/
|-- run.py
|-- requirements.txt
|-- .env
`-- README.md
```

## Instalação

### 1. Clonar repositório

```bash
git clone <seu-repositorio>
cd "Streaming Music"
```

### 2. Criar e ativar ambiente virtual

```bash
python -m venv venv

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

Recomendado no Windows (garante instalação no ambiente correto):

```bash
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
FLASK_APP=run.py
FLASK_ENV=development

APP_NAME=Vitorando Music
SECRET_KEY=sua-chave-secreta
APP_BASE_URL=http://localhost:5000

DATABASE_URL=sqlite:///streaming_music.db
DEFAULT_TENANT_SLUG=default
DEFAULT_TENANT_NAME=Workspace Padrao

REQUIRE_EMAIL_VERIFICATION=false
AUTO_VERIFY_EMAIL=true
PASSWORD_RESET_TOKEN_EXP_HOURS=1

RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=120

STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID_FREE=price_xxx_free
STRIPE_PRICE_ID_PRO=price_xxx_pro
STRIPE_PRICE_ID_BUSINESS=price_xxx_business

EMAIL_DELIVERY_ENABLED=false
SMTP_HOST=smtp.seuprovedor.com
SMTP_PORT=587
SMTP_USERNAME=usuario
SMTP_PASSWORD=senha
SMTP_USE_TLS=true
SMTP_USE_SSL=false
MAIL_FROM=no-reply@streamingmusic.local

SENTRY_DSN=
```

Observações:

- Se `DATABASE_URL` não for informada, o projeto usa SQLite local em `instance/streaming_music.db`.
- Para produção, use PostgreSQL em `DATABASE_URL`.
- Em produção, recomenda-se `REQUIRE_EMAIL_VERIFICATION=true`.

## Banco de Dados e Migrations

```bash
# aplicar todas as migrations
flask --app run.py db upgrade

# inicializar tabelas (modo rápido local)
flask --app run.py init-db

# resetar e popular banco com seed de demo
flask --app run.py seed-db

# sincronizar stripe_price_id dos planos via .env
flask --app run.py sync-stripe-prices
```

Migrations SaaS adicionadas:

- `004_create_plans`
- `005_create_subscriptions`
- `006_create_usage_events_and_limits`
- `007_add_email_verification_fields`
- `008_create_audit_logs`
- `009_add_api_keys_or_access_tokens`

## Seed de Demo

O comando `seed-db`:

- remove e recria tabelas (`drop_all` + `create_all`)
- cria tenant default
- cria 2 usuários de demo
- cria memberships
- cria 3 planos (`free`, `pro`, `business`)
- cria assinatura ativa para o tenant default
- cria 5 artistas, 5 álbuns e 20 músicas
- cria 3 playlists
- gera 20 arquivos de áudio `.wav` em `app/static/music`

Credenciais de demo:

- `demo@streamingmusic.local` / `123456`
- `curador@streamingmusic.local` / `123456`

## Executando a Aplicação

```bash
# opção direta
python run.py

# opção Flask CLI
flask --app run.py run --debug
```

Aplicação: [http://localhost:5000](http://localhost:5000)

## Endpoints da API (resumo)

### Músicas

- `GET /api/musicas`
- `GET /api/musicas/<id>`
- `GET /api/musicas/populares`
- `POST /api/musicas/<id>/reproduzir`

### Playlists

- `GET /api/playlists`
- `POST /api/playlists`
- `GET /api/playlists/<id>`
- `PUT /api/playlists/<id>`
- `DELETE /api/playlists/<id>`
- `POST /api/playlists/<id>/musicas/<mid>`
- `DELETE /api/playlists/<id>/musicas/<mid>`
- `GET /api/playlists/publicas`

### Billing

- `GET /api/billing/plans`
- `GET /api/billing/subscription`
- `POST /api/billing/checkout`
- `POST /api/billing/portal`
- `POST /api/billing/webhook`

### Auth e Segurança

- `POST /api/auth/verificar-email`
- `POST /api/auth/solicitar-reset`
- `POST /api/auth/redefinir-senha`

### Usuário

- `GET /api/usuario/perfil`
- `PUT /api/usuario/perfil`
- `POST /api/usuario/favoritos/<id>`
- `DELETE /api/usuario/favoritos/<id>`

## Tela de Planos (Web)

- `GET /billing/planos` (login obrigatório)
- `POST /billing/planos/trocar` (troca de plano pela interface)

Comportamento de troca:

- `free`: troca imediata
- `pro` e `business`: usa checkout Stripe quando configurado
- em ambiente de desenvolvimento/teste sem Stripe, permite troca local para facilitar validação

## Stripe: Fluxo Rápido

1. Configure `STRIPE_SECRET_KEY` e `STRIPE_WEBHOOK_SECRET`.
2. Preencha `STRIPE_PRICE_ID_FREE`, `STRIPE_PRICE_ID_PRO` e `STRIPE_PRICE_ID_BUSINESS`.
3. Rode `flask --app run.py sync-stripe-prices` para atualizar o banco.
4. Chame `POST /api/billing/checkout` para iniciar assinatura.
5. Aponte o webhook Stripe para `POST /api/billing/webhook`.
6. O sistema sincroniza status da assinatura por tenant.

## Segurança e Observabilidade

- login pode exigir e-mail verificado (`REQUIRE_EMAIL_VERIFICATION`)
- reset de senha por token com expiração
- envio real de e-mail via SMTP para verificação/reset (`EMAIL_DELIVERY_ENABLED=true`)
- auditoria de eventos sensíveis em `audit_logs`
- suporte para API keys por tenant
- rate limit para rotas `/api/*` (exceto webhook Stripe)
- log de duração por request (`X-Request-Duration-Ms`)
- integração opcional com Sentry via `SENTRY_DSN`

## Testes

```bash
# executa a suíte principal
python -m unittest tests/test_application.py

# modo verboso com resumo APROVADO/REPROVADO
python tests/test_application.py
```

## Deploy (referência rápida)

Exemplo com Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

Checklist recomendado para produção:

1. `DATABASE_URL` em PostgreSQL
2. `SECRET_KEY` forte
3. `REQUIRE_EMAIL_VERIFICATION=true`
4. `STRIPE_*` configurado
5. `SENTRY_DSN` (opcional)
6. `flask --app run.py db upgrade` antes de subir

## Troubleshooting

### `ModuleNotFoundError: No module named 'app'`

1. Execute comandos na raiz do projeto (`Streaming Music`).
2. Prefira `flask --app run.py ...`.
3. Se rodar a partir da pasta pai, use aspas por causa do espaço:

```bash
flask --app "Streaming Music.run" routes
```

### Áudio não toca no player

1. Rode `flask --app run.py seed-db` para garantir arquivos em `app/static/music`.
2. Verifique o caminho de `arquivo_url`.
3. Teste URL direta no navegador, por exemplo:

```text
http://localhost:5000/static/music/aurora-pulse-neon-nights-01-city-lights.wav
```

### `Biblioteca stripe nao instalada no ambiente`

Esse erro normalmente indica instalação fora do `venv` ativo.

```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe -c "import stripe; print(stripe._version.VERSION)"
```

### Deploy sobe, mas cai com `Exited with status 1` no Render

1. Confirme `DATABASE_URL` configurada no servico.
2. Confirme `FLASK_ENV=production`.
3. Fixe a versao de Python para 3.12 (ou superior) no Render.
4. Rode no Shell do Render:

```bash
flask --app run.py db upgrade
flask --app run.py bootstrap-deploy
```

### `ImportError ... psycopg2 ... undefined symbol: _PyInterpreterState_Get`

Esse erro costuma acontecer quando o deploy usa Python 3.14 com `psycopg2-binary` antigo.

1. Fixe a versao para Python 3.12.
2. Limpe cache de build e redeploy.
3. Verifique nos logs se os wheels nao estao mais como `cp314`.

## Licença

Uso educacional.

## Deploy Render + Neon (Free)

This repository now includes `render.yaml` for Render Blueprint deployment.

### 1. Create infrastructure

1. Create a PostgreSQL database on Neon and copy `DATABASE_URL`.
2. Create a Web Service on Render from this repository (or use Blueprint sync).
3. Set the required secrets in Render:
   - `DATABASE_URL`
   - `APP_BASE_URL`
   - `STRIPE_*` values

### 2. Build and start commands

- Build: `pip install -r requirements.txt`
- Start: `gunicorn run:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120`

### 3. First deploy bootstrap (safe / non-destructive)

Run these commands once in the Render Shell:

```bash
flask --app run.py db upgrade
flask --app run.py bootstrap-deploy
```

Optional (if you changed Stripe Price IDs later):

```bash
flask --app run.py sync-stripe-prices
```

### 4. New CLI commands

- `flask --app run.py ensure-plans`
  - upserts `free`, `pro`, `business` plans without deleting data.
- `flask --app run.py bootstrap-deploy`
  - ensures DB tables, default tenant, base plans, and Stripe price sync.

### 5. Stripe webhook

Set your Stripe webhook endpoint to:

```text
https://<your-render-domain>/api/billing/webhook
```

Recommended events:

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

## Render MCP (AI Build Debug)

To debug failed deploys with AI tools (Cursor / Claude Code), connect Render MCP and use prompts like:

- `Show my latest failed deploy logs for <service-name>`
- `Diagnose root cause and propose exact build/start/env fixes`
- `List missing environment variables used by this Flask app`
