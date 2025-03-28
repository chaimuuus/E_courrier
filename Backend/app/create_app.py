from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import Config
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager  # ✅ Ajout de l'importation

db = SQLAlchemy()
bcrypt = Bcrypt()
socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ✅ Initialisation correcte de JWTManager
    jwt = JWTManager(app)
    
    db.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)

    from .routers.auth import auth_bp
    # 💡 Importer les modèles avant de créer les tables
    from .models import Utilisateur, Contact, Courrier, Document, Workflow  

    with app.app_context():
        db.create_all()
        app.register_blueprint(auth_bp, url_prefix="/auth")
        print("✅ Tables créées avec succès !")

    return app
