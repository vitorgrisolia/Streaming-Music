# 🎵 Plataforma de Streaming de Música

Sistema completo de streaming de música desenvolvido com Flask seguindo o padrão MVC (Model-View-Controller).

## 📋 Características

- ✅ Autenticação e gerenciamento de usuários
- ✅ Busca e reprodução de músicas
- ✅ Criação e gerenciamento de playlists
- ✅ Sistema de favoritos
- ✅ Visualização de artistas e álbuns
- ✅ API RESTful completa
- ✅ Arquitetura MVC bem definida
- ✅ Banco de dados PostgreSQL
- ✅ Relacionamentos complexos entre entidades

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.8+**
- **Flask** - Framework web
- **Flask-SQLAlchemy** - ORM para banco de dados
- **Flask-Login** - Gerenciamento de sessões
- **Flask-Bcrypt** - Criptografia de senhas
- **PostgreSQL** - Banco de dados relacional

### Frontend
- **HTML5**
- **CSS3**
- **JavaScript**

## 📁 Estrutura do Projeto

```
music-platform/
├── app/
│   ├── __init__.py              # Factory da aplicação
│   ├── extensions.py            # Extensões do Flask
│   ├── models/                  # Camada de Dados (Model)
│   │   ├── user.py             # Model de Usuário
│   │   ├── artist.py           # Model de Artista
│   │   ├── album.py            # Model de Álbum
│   │   ├── music.py            # Model de Música
│   │   └── playlist.py         # Model de Playlist
│   ├── controllers/             # Lógica de Negócio (Controller)
│   │   ├── auth_controller.py
│   │   ├── music_controller.py
│   │   └── playlist_controller.py
│   ├── views/                   # Rotas e Apresentação (View)
│   │   ├── auth_routes.py
│   │   ├── music_routes.py
│   │   ├── playlist_routes.py
│   │   └── api_routes.py
│   ├── static/                  # Arquivos estáticos
│   │   ├── css/
│   │   └── js/
│   └── templates/               # Templates HTML
├── config/
│   └── settings.py             # Configurações da aplicação
├── requirements.txt
├── run.py                      # Arquivo principal
└── .env.example               # Exemplo de variáveis de ambiente
```

## 🚀 Instalação e Configuração

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd music-platform
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados PostgreSQL

```bash
# Entre no PostgreSQL
psql -U postgres

# Crie o banco de dados
CREATE DATABASE music_platform_dev;
CREATE USER seu_usuario WITH PASSWORD '123';
GRANT ALL PRIVILEGES ON DATABASE music_platform_dev TO seu_usuario;
```

### 5. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e edite com suas configurações:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/music_platform_dev
```

### 6. Inicialize o banco de dados

```bash
# Criar as tabelas
flask init-db

# Popular com dados de exemplo (opcional)
flask seed-db
```

### 7. Execute a aplicação

```bash
python run.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 👤 Credenciais de Teste

Se você executou o comando `flask seed-db`, use estas credenciais:

- **Email:** teste@email.com
- **Senha:** senha123

## 📊 Modelo de Dados

### Entidades Principais

1. **Usuários** - Gerenciamento de contas
2. **Artistas** - Informações sobre artistas
3. **Álbuns** - Coleções de músicas
4. **Músicas** - Faixas individuais
5. **Playlists** - Coleções personalizadas de músicas

### Relacionamentos

- Um **Artista** possui vários **Álbuns**
- Um **Álbum** pertence a um **Artista** e possui várias **Músicas**
- Uma **Música** pertence a um **Álbum**
- Um **Usuário** pode criar várias **Playlists**
- Uma **Playlist** pode conter várias **Músicas** (relacionamento N:N)
- Um **Usuário** pode favoritar várias **Músicas** (relacionamento N:N)

## 🔌 API REST

### Endpoints de Músicas

```
GET    /api/musicas                    # Lista todas as músicas
GET    /api/musicas/<id>               # Detalhes de uma música
GET    /api/musicas/populares          # Músicas mais populares
POST   /api/musicas/<id>/reproduzir    # Registra reprodução
```

### Endpoints de Playlists

```
GET    /api/playlists                        # Lista playlists do usuário
POST   /api/playlists                        # Cria nova playlist
GET    /api/playlists/<id>                   # Detalhes da playlist
PUT    /api/playlists/<id>                   # Atualiza playlist
DELETE /api/playlists/<id>                   # Deleta playlist
POST   /api/playlists/<id>/musicas/<mid>     # Adiciona música
DELETE /api/playlists/<id>/musicas/<mid>     # Remove música
GET    /api/playlists/publicas               # Lista playlists públicas
```

### Endpoints de Usuário

```
GET    /api/usuario/perfil                   # Perfil do usuário
PUT    /api/usuario/perfil                   # Atualiza perfil
POST   /api/usuario/favoritos/<id>           # Adiciona favorito
DELETE /api/usuario/favoritos/<id>           # Remove favorito
```

## 🧪 Comandos Flask CLI

```bash
# Inicializar banco de dados
flask init-db

# Popular com dados de exemplo
flask seed-db

# Abrir shell interativo com contexto da aplicação
flask shell
```

## 🏗️ Padrão MVC Implementado

### Model (Modelos)
- Define a estrutura de dados
- Gerencia interações com o banco de dados
- Implementa lógica de negócio específica de entidades
- Localização: `app/models/`

### View (Visões)
- Define rotas da aplicação
- Processa requisições HTTP
- Renderiza templates
- Retorna respostas JSON (API)
- Localização: `app/views/`

### Controller (Controladores)
- Contém a lógica de negócio
- Processa dados entre Model e View
- Valida entradas
- Gerencia transações
- Localização: `app/controllers/`

## 🔒 Segurança

- ✅ Senhas criptografadas com Bcrypt
- ✅ Proteção contra CSRF
- ✅ Sessões seguras com cookies HTTP-only
- ✅ Validação de dados de entrada
- ✅ Autenticação obrigatória para operações sensíveis

## 🚀 Deploy em Produção

### Configurações recomendadas:

1. Use um servidor WSGI como **Gunicorn**
2. Configure um proxy reverso com **Nginx**
3. Use **PostgreSQL** em produção
4. Configure variáveis de ambiente adequadas
5. Ative HTTPS
6. Configure backups regulares do banco de dados

### Exemplo com Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## 📝 Licença

Este projeto é de código aberto e está disponível para fins educacionais.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

## 📧 Contato

Para dúvidas ou sugestões, entre em contato através do repositório.

---

**Desenvolvido Vitor Grisolia usando Flask e Python**