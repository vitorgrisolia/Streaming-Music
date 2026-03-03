from flask import Flask

from app.extensions import db, init_extensions


def create_app():
    app = Flask(__name__)

    # Configurações
    app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///streaming_music.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa extensões
    init_extensions(app)

    # Registra blueprints
    from app.views.auth_routes import auth_bp
    from app.views.music_routes import music_bp
    from app.views.playlist_routes import playlist_bp
    from app.views.api_routes import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(music_bp)
    app.register_blueprint(playlist_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Cria tabelas se não existirem
    with app.app_context():
        db.create_all()

    return app
