from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, JWTManager
)
from ..models import Utilisateur
from ..create_app import db
from datetime import timedelta
import logging

# Initialisation du Blueprint et des outils
auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/')
def home():
    return jsonify({"message": "Hey Chaimuus!"}), 200

# 📝 INSCRIPTION (Seulement pour l'admin)
@auth_bp.route('/register', methods=['POST'])
@jwt_required()  # Seuls les admins peuvent ajouter un utilisateur
def register():
    current_user = get_jwt_identity()
    if current_user["role"] != "admin":
        return jsonify({"message": "Accès refusé"}), 403

    data = request.get_json()
    
    # Vérification des données
    required_fields = ["nom", "prenom", "email", "password", "numero_tel"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"message": f"{field} est requis"}), 400

    # Vérifier si l'email est déjà utilisé
    if Utilisateur.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email déjà utilisé"}), 400

    # Hash du mot de passe
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode('utf-8')

    # Création de l'utilisateur
    new_user = Utilisateur(
        nom=data["nom"],
        prenom=data["prenom"],
        email=data["email"],
        mot_de_passe=hashed_password,
        numero_tel=data["numero_tel"],
        role=data.get("role", "employe")  # Par défaut, employé
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Utilisateur créé avec succès"}), 201

# 🔑 CONNEXION
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if "email" not in data or "password" not in data:
        return jsonify({"message": "Email et mot de passe requis"}), 400

    utilisateur = Utilisateur.query.filter_by(email=data["email"]).first()
    
    if not utilisateur or not bcrypt.check_password_hash(utilisateur.mot_de_passe, data["password"]):
        return jsonify({"message": "Identifiants incorrects"}), 401

    # Générer un token JWT avec une expiration de 2 jours
    access_token = create_access_token(
        identity={"id": utilisateur.id, "role": utilisateur.role},
        expires_delta=timedelta(days=2)
    )
    
    return jsonify({
        "access_token": access_token,
        "role": utilisateur.role
    })

# 🚪 DÉCONNEXION (Le client supprime simplement le token)
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Déconnexion réussie"}), 200
