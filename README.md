# Streaming Music Platform

Aplicacao web de streaming de musica com Flask (MVC), interface web, API REST e suporte SaaS com multi-tenant, planos, cobranca e seguranca reforcada.

## Visao Geral

O projeto inclui:

- autenticacao e sessao de usuarios
- verificacao de e-mail e reset de senha por token
- catalogo de artistas, albuns e musicas
- player HTML5 para reproducao de audio
- criacao e gerenciamento de playlists
- favoritos por usuario
- isolamento por tenant (multi-tenant)
- planos (`Plan`) e assinatura por tenant (`Subscription`)
- eventos de uso para controle de limite (`UsageEvent`)
- webhook Stripe para sincronizar cobranca
- auditoria de eventos sensiveis (`AuditLog`)
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

## Instalacao

### 1. Clonar repositorio

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

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Recomendado no Windows (garante instalacao no ambiente correto):

```bash
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configurar variaveis de ambiente

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

Observacoes:

- Se `DATABASE_URL` nao for informada, o projeto usa SQLite local em `instance/streaming_music.db`.
- Para producao, use PostgreSQL em `DATABASE_URL`.
- Em producao, recomenda-se `REQUIRE_EMAIL_VERIFICATION=true`.

## Banco de Dados e Migrations

```bash
# aplicar todas as migrations
flask --app run.py db upgrade

# inicializar tabelas (modo rapido local)
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
- cria 2 usuarios de demo
- cria memberships
- cria 3 planos (`free`, `pro`, `business`)
- cria assinatura ativa para o tenant default
- cria 5 artistas, 5 albuns e 20 musicas
- cria 3 playlists
- gera 20 arquivos de audio `.wav` em `app/static/music`

Credenciais de demo:

- `demo@streamingmusic.local` / `123456`
- `curador@streamingmusic.local` / `123456`

## Executando a Aplicacao

```bash
# opcao direta
python run.py

# opcao Flask CLI
flask --app run.py run --debug
```

Aplicacao: [http://localhost:5000](http://localhost:5000)

## Endpoints da API (resumo)

### Musicas

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

## Tela de Planos (Web)

- `GET /billing/planos` (login obrigatorio)
- `POST /billing/planos/trocar` (troca de plano pela interface)

Comportamento de troca:

- `free`: troca imediata
- `pro` e `business`: usa checkout Stripe quando configurado
- em ambiente de desenvolvimento/teste sem Stripe, permite troca local para facilitar validacao

### Auth e Seguranca

- `POST /api/auth/verificar-email`
- `POST /api/auth/solicitar-reset`
- `POST /api/auth/redefinir-senha`

### Usuario

- `GET /api/usuario/perfil`
- `PUT /api/usuario/perfil`
- `POST /api/usuario/favoritos/<id>`
- `DELETE /api/usuario/favoritos/<id>`

## Stripe: Fluxo Rapido

1. Configure `STRIPE_SECRET_KEY` e `STRIPE_WEBHOOK_SECRET`.
2. Preencha `STRIPE_PRICE_ID_FREE`, `STRIPE_PRICE_ID_PRO` e `STRIPE_PRICE_ID_BUSINESS`.
3. Rode `flask --app run.py sync-stripe-prices` para atualizar o banco.
4. Chame `POST /api/billing/checkout` para iniciar assinatura.
5. Aponte o webhook Stripe para `POST /api/billing/webhook`.
6. O sistema sincroniza status da assinatura por tenant.

## Seguranca e Observabilidade

- login pode exigir e-mail verificado (`REQUIRE_EMAIL_VERIFICATION`)
- reset de senha por token com expiracao
- envio real de email via SMTP para verificacao/reset (`EMAIL_DELIVERY_ENABLED=true`)
- auditoria de eventos sensiveis em `audit_logs`
- suporte para API keys por tenant
- rate limit para rotas `/api/*` (exceto webhook Stripe)
- log de duracao por request (`X-Request-Duration-Ms`)
- integracao opcional com Sentry via `SENTRY_DSN`

## Testes

```bash
# executa a suite principal
python -m unittest tests/test_application.py

# modo verboso com resumo APROVADO/REPROVADO
python tests/test_application.py
```

## Deploy (referencia rapida)

Exemplo com Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

Checklist recomendado para producao:

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
3. Se rodar a partir da pasta pai, use aspas por causa do espaco:

```bash
flask --app "Streaming Music.run" routes
```

### Audio nao toca no player

1. Rode `flask --app run.py seed-db` para garantir arquivos em `app/static/music`.
2. Verifique o caminho de `arquivo_url`.
3. Teste URL direta no navegador, por exemplo:

```text
http://localhost:5000/static/music/aurora-pulse-neon-nights-01-city-lights.wav
```

### `Biblioteca stripe nao instalada no ambiente`

Esse erro normalmente indica instalacao fora do `venv` ativo.

```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe -c "import stripe; print(stripe._version.VERSION)"
```

## Licenca

Uso educacional.
