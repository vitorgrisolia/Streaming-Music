# Streaming Music Platform

Aplicacao web de streaming de musica com Flask (MVC), interface web, API REST e suporte SaaS com multi-tenant, planos, cobranca e seguranca reforcada.

## Visao geral

Este projeto inclui:

- autenticacao e sessao de usuarios
- verificacao de e-mail e reset de senha por token
- catalogo de artistas, albuns e musicas
- player HTML5
- criacao e gerenciamento de playlists
- favoritos por usuario
- isolamento por tenant (multi-tenant)
- planos (`Plan`) e assinaturas (`Subscription`)
- eventos de uso (`UsageEvent`) para controle de limite
- webhook Stripe para sincronizar cobranca
- auditoria (`AuditLog`)
- API keys por tenant (`ApiKey`)
- rate limit para `/api/*` e observabilidade por request

## Stack

- Python 3.12 (recomendado)
- Flask 3
- Flask-SQLAlchemy
- Flask-Migrate (Alembic)
- Flask-Login
- Flask-Bcrypt
- Flask-CORS
- Stripe SDK
- sentry-sdk (opcional)
- python-dotenv
- gunicorn

## Estrutura do projeto

```text
Streaming Music/
|-- app/
|   |-- __init__.py
|   |-- config/settings.py
|   |-- controllers/
|   |-- models/
|   |-- services/
|   |-- templates/
|   |-- static/
|   `-- views/
|-- migrations/
|-- tests/
|-- run.py
|-- requirements.txt
|-- render.yaml
|-- .python-version
|-- .env.example
`-- README.md
```

## Requisitos

- Python 3.12
- Git
- (Opcional) conta Stripe para billing real
- (Producao) PostgreSQL (ex.: Neon)

## Setup local

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

### 4. Configurar variaveis

Use `.env.example` como base e crie `.env` local.

Exemplo minimo local:

```env
FLASK_APP=run.py
FLASK_ENV=development
APP_NAME=Vitorando Music
SECRET_KEY=change-me
APP_BASE_URL=http://localhost:5000
DATABASE_URL=sqlite:///streaming_music.db
DEFAULT_TENANT_SLUG=default
DEFAULT_TENANT_NAME=Workspace Padrao
```

## Variaveis de ambiente

### Obrigatorias em producao

- `DATABASE_URL`
- `APP_BASE_URL`
- `SECRET_KEY`

### Recomendadas em producao

- `FLASK_ENV=production`
- `PYTHON_DOTENV_DISABLED=1`
- `REQUIRE_EMAIL_VERIFICATION=true`
- `AUTO_VERIFY_EMAIL=false`
- `RATE_LIMIT_ENABLED=true`
- `RATE_LIMIT_REQUESTS_PER_MINUTE=120`

### Stripe

- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID_FREE`
- `STRIPE_PRICE_ID_PRO`
- `STRIPE_PRICE_ID_BUSINESS`

### SMTP (opcional)

- `EMAIL_DELIVERY_ENABLED`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`
- `SMTP_USE_SSL`
- `MAIL_FROM`

### Observabilidade

- `SENTRY_DSN` (opcional)

## Comandos CLI

```bash
# aplica migrations
flask --app run.py db upgrade

# inicializa banco e garante tenant default + planos base
flask --app run.py init-db

# garante planos sem apagar dados
flask --app run.py ensure-plans

# sincroniza stripe_price_id dos planos via env
flask --app run.py sync-stripe-prices

# bootstrap seguro para primeiro deploy (nao destrutivo)
flask --app run.py bootstrap-deploy

# seed demo (destrutivo: drop_all + create_all)
flask --app run.py seed-db
```

## Seed demo

`seed-db` cria dados de demonstracao, incluindo:

- tenant default
- usuarios demo
- planos free/pro/business
- assinatura ativa no tenant default
- catalogo de musicas e playlists
- arquivos `.wav` em `app/static/music`

Credenciais demo:

- `demo@streamingmusic.local / 123456`
- `curador@streamingmusic.local / 123456`

## Executar aplicacao

```bash
# modo direto
python run.py

# Flask CLI (debug)
flask --app run.py run --debug
```

Aplicacao local: [http://localhost:5000](http://localhost:5000)

## Testes

```bash
python -m unittest tests/test_application.py
```

## Endpoints (resumo)

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

### Auth

- `POST /api/auth/verificar-email`
- `POST /api/auth/solicitar-reset`
- `POST /api/auth/redefinir-senha`

### Usuario

- `GET /api/usuario/perfil`
- `PUT /api/usuario/perfil`
- `POST /api/usuario/favoritos/<id>`
- `DELETE /api/usuario/favoritos/<id>`

## Deploy em nuvem (Render + Neon)

Este repositorio inclui `render.yaml` para Blueprint no Render.

### 1. Banco (Neon)

1. Crie um projeto no Neon.
2. Copie a URL de conexao PostgreSQL.
3. Use formato recomendado:

```text
postgresql://user:password@host:5432/dbname?sslmode=require
```

### 2. Servico web (Render)

No Render, crie um `Web Service` para este repositorio.

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
python -m gunicorn run:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120
```

### 3. Fixar versao do Python

- O projeto usa `.python-version` com `3.12`.
- No Render, mantenha tambem `PYTHON_VERSION=3.12` em `Environment`.

### 4. Variaveis obrigatorias no Render

- `DATABASE_URL`
- `APP_BASE_URL`
- `SECRET_KEY`

Tambem configure:

- `FLASK_ENV=production`
- `PYTHON_DOTENV_DISABLED=1`

### 5. Primeiro bootstrap apos deploy

No Shell do Render:

```bash
flask --app run.py db upgrade
flask --app run.py bootstrap-deploy
```

### 6. Stripe webhook

Endpoint:

```text
https://<seu-dominio-render>/api/billing/webhook
```

Eventos recomendados:

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

## Render MCP (debug com IA)

Guia rapido em [docs/render-mcp.md](docs/render-mcp.md).

Resumo:

- Cursor: configurar `~/.cursor/mcp.json`
- Claude Code: `claude mcp add ...`
- Prompts uteis: logs de deploy, causa raiz, sugestao de fix em env/build/start

## Troubleshooting

### `Exited with status 127`

Causa comum: comando de start nao encontrado.

Use:

```bash
python -m gunicorn run:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120
```

### `Exited with status 1`

Normalmente erro na inicializacao da app (env, DB, import).

Checklist:

1. `DATABASE_URL` existe e esta valida.
2. `FLASK_ENV=production`.
3. `PYTHON_VERSION=3.12`.
4. Rode no shell:

```bash
python - <<'PY'
import os
print('DATABASE_URL set?', bool(os.getenv('DATABASE_URL')))
from run import app
print('APP_OK')
PY
```

### `SQLALCHEMY_DATABASE_URI nao configurado para o ambiente atual`

`DATABASE_URL` ausente ou vazia em producao.

### `ImportError ... psycopg2 ... undefined symbol: _PyInterpreterState_Get`

Causa: runtime Python 3.14 com wheel `psycopg2-binary` incompativel.

Correcao:

1. Fixar Python 3.12.
2. `Clear build cache & deploy`.
3. Confirmar logs sem `cp314`.

### `UnicodeDecodeError: 'utf-8' codec can't decode byte ...`

Causa comum: leitura de `.env` com codificacao invalida em ambiente de deploy.

Correcao:

1. `PYTHON_DOTENV_DISABLED=1`
2. garantir `FLASK_ENV=production`
3. redeploy com cache limpo

Obs.: o app ja ignora `.env` automaticamente em Render (`RENDER=true`).

### `ModuleNotFoundError: No module named 'app'`

- Execute comandos na raiz do projeto.
- Prefira `flask --app run.py ...`.

### Audio nao toca no player

1. Rode `flask --app run.py seed-db` para gerar arquivos demo.
2. Verifique `arquivo_url` salvo no banco.

## Seguranca (producao)

- use `SECRET_KEY` forte
- use PostgreSQL gerenciado
- habilite verificacao de e-mail (`REQUIRE_EMAIL_VERIFICATION=true`)
- configure Stripe webhook com segredo valido
- use HTTPS no dominio final
- habilite Sentry (opcional)

## Limitacoes do plano gratis

- Render free pode entrar em sleep sem trafego
- primeira requisicao apos idle pode ter cold start
- evite depender de filesystem local para dados permanentes

## Licenca

Uso educacional.
