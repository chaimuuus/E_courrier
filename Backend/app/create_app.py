from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import Config
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_session import Session
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
socketio = SocketIO()
jwt = JWTManager()
sess = Session()  # ✅ Garde l'instance en dehors de create_app()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # ✅ Charge la config depuis ton fichier Config
    app.config["SESSION_TYPE"] = "filesystem"  # Permet de stocker la session côté serveur
    app.secret_key = "un_secret_aleatoire"
    app.config["JWT_SECRET_KEY"] = "chaima"

    # Initialisation correcte des extensions
    sess.init_app(app)  # ✅ Utilise l'instance globale
    db.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)
    jwt.init_app(app)  # ✅ Ne pas recréer une nouvelle instance ici !

    from .routers.auth import auth_bp
    from .routers.contact import google_bp
    from .routers.courrier import courrier_bp
    from .models import Utilisateur, Contact, Courrier, Document, Workflow  

    with app.app_context():
        db.create_all()
        app.register_blueprint(auth_bp, url_prefix="/auth")
        app.register_blueprint(google_bp)
        app.register_blueprint(courrier_bp)
        print("✅ Tables créées avec succès !")

    # ✅ Test si la session fonctionne
    @app.route("/set-test-session")
    def set_test_session():
        session["test"] = "OK"
        return "Session enregistrée."

    @app.route("/get-test-session")
    def get_test_session():
        return f"Valeur en session : {session.get('test', '❌ Rien trouvé')}"

    return app
