from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import Config
from flask_socketio import SocketIO

db = SQLAlchemy()
bcrypt = Bcrypt()
socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)

    # 💡 Ici tu dois importer tous tes models AVANT db.create_all()
    from .models import Utilisateur, Contact, Categorie, Courrier, Document, Workflow
    
    with app.app_context():
        db.create_all()
        print("✅ Tables créées avec succès !")

    return app
