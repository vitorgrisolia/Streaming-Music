# Streaming Music Platform

Aplicacao web de streaming de musica com Flask (padrao MVC), com interface web, API REST e seed completo para ambiente de demo.

## Visao Geral

O projeto inclui:

- autenticacao e sessao de usuarios
- catalogo de artistas, albuns e musicas
- player HTML5 para reproducao de audio
- criacao e gerenciamento de playlists
- favoritos por usuario
- API REST para musicas, playlists e perfil
- seed completo com 20 musicas tocaveis

## Stack

- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-Bcrypt
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
|   |-- models/
|   |-- views/
|   |-- templates/
|   `-- static/
|       |-- css/
|       |-- js/
|       `-- music/            # arquivos .wav gerados pelo seed
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

### 4. Configurar variaveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta
DATABASE_URL=sqlite:///streaming_music.db
```

Observacoes:

- Se `DATABASE_URL` nao for informada, o projeto usa SQLite local em `instance/streaming_music.db`.
- Para PostgreSQL, use uma URL no formato `postgresql://usuario:senha@host:5432/banco`.

## Executando a Aplicacao

### Opcao 1: executar diretamente

```bash
python run.py
```

### Opcao 2: via Flask CLI

```bash
flask --app run.py run --debug
```

Aplicacao disponivel em: [http://localhost:5000](http://localhost:5000)

## Comandos Flask

```bash
# criar tabelas
flask --app run.py init-db

# resetar e popular banco com seed completo
flask --app run.py seed-db

# shell com contexto da aplicacao
flask --app run.py shell
```

## Seed Completo (20 musicas tocaveis)

O comando `seed-db`:

- remove e recria as tabelas (`drop_all` + `create_all`)
- cria 2 usuarios de demo
- cria 5 artistas e 5 albuns
- cria 20 musicas
- cria 3 playlists
- gera 20 arquivos de audio `.wav` em `app/static/music`

Credenciais geradas pelo seed:

- `demo@streamingmusic.local` / `123456`
- `curador@streamingmusic.local` / `123456`

Playlists de exemplo:

- `Top 20 do Streaming Music` (publica)
- `Favoritas da Semana` (privada do usuario demo)
- `Foco no Trabalho` (publica)

## Testes

```bash
python -m unittest tests/test_application.py
```

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

### Usuario

- `GET /api/usuario/perfil`
- `PUT /api/usuario/perfil`
- `POST /api/usuario/favoritos/<id>`
- `DELETE /api/usuario/favoritos/<id>`

## Troubleshooting

### `ModuleNotFoundError: No module named 'app'`

Use uma destas abordagens:

1. Execute comandos a partir da pasta raiz do projeto (`Streaming Music`).
2. Prefira `flask --app run.py ...` em vez de imports de modulo ambiguos.
3. Se rodar Flask a partir da pasta pai, use aspas no app path por causa do espaco no nome da pasta:

```bash
flask --app "Streaming Music.run" routes
```

### Audio nao toca no player

1. Rode novamente `flask --app run.py seed-db` para garantir os arquivos em `app/static/music`.
2. Verifique se o arquivo da musica existe no caminho retornado por `arquivo_url`.
3. Abra diretamente uma URL de audio no navegador, por exemplo:

```text
http://localhost:5000/static/music/aurora-pulse-neon-nights-01-city-lights.wav
```

## Deploy (referencia rapida)

Exemplo com Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## Licenca

Uso educacional.
