from flask import Blueprint, redirect, request, session, jsonify, make_response
from google_auth_oauthlib.flow import Flow
import os
from ..models import Contact, Utilisateur  # Import de la classe Utilisateur
import requests
from googleapiclient.discovery import build
from flask_sqlalchemy import SQLAlchemy
from ..create_app import db  # Assurez-vous que db est bien importé
from flask_jwt_extended import jwt_required
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
google_bp = Blueprint('google_auth', __name__)

# 📌 Autoriser HTTP pour OAuth en local
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
SECRET_KEY = "chaima"
# 📌 Vérification du fichier credentials.json
CREDENTIALS_FILE = "C:/Users/User/OneDrive/Documents/E_courrier/E_courrier/Backend/app/credentials.json"
if not os.path.exists(CREDENTIALS_FILE):
    raise FileNotFoundError(f"Fichier credentials.json introuvable : {CREDENTIALS_FILE}")

flow = Flow.from_client_secrets_file(
    CREDENTIALS_FILE,
    scopes=["https://www.googleapis.com/auth/contacts.readonly"],
    redirect_uri="http://localhost:5000/callback"
)
 

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }



@google_bp.route("/google-login")
def google_login():
    """Redirige vers la page d'authentification Google."""
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)

@google_bp.route("/callback")
def callback():
    try:
        flow.fetch_token(authorization_response=request.url)
        session["credentials"] = credentials_to_dict(flow.credentials)
        session.modified = True
        return redirect("/contacts")
    except Exception as e:
        return jsonify({"error": "Erreur lors de l'authentification", "details": str(e)}), 403

@google_bp.route("/contacts")
def contacts():
    """Récupère les contacts depuis l'API Google People."""

    credentials = session.get("credentials")
    if not credentials:
        return redirect("/google-login")

    access_token = credentials.get("token")
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://people.googleapis.com/v1/people/me/connections?personFields=names,emailAddresses"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Impossible de récupérer les contacts", "details": response.text}), response.status_code

from google.oauth2.credentials import Credentials

@google_bp.route("/import-contacts")
def import_contacts():
   

    if "credentials" not in session:
        return jsonify({"error": "Utilisateur non connecté à Google"}), 401

    try:
        credentials = Credentials(**session["credentials"])
        service = build("people", "v1", credentials=credentials)
        results = service.people().connections().list(
            resourceName="people/me",
            personFields="names,emailAddresses"
        ).execute()

        contacts = []
        for person in results.get("connections", []):
            noms = person.get("names", [])
            emails = person.get("emailAddresses", [])
            
            if noms and emails:
                prenom = noms[0].get("givenName", "Inconnu")
                email = emails[0].get("value", None)
                contacts.append({"prenom": prenom, "email": email})

        session["contacts"] = contacts
        return jsonify({"contacts": contacts}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@google_bp.route("/save-contacts", methods=["POST"])
def save_contacts():

    data = request.json
    selected_contacts = data.get("contacts", [])

    if not selected_contacts:
        return jsonify({"error": "Aucun contact sélectionné"}), 400

    for contact in selected_contacts:
        prenom = contact.get("prenom")
        email = contact.get("email")

        if not Contact.query.filter_by(email=email).first():
            new_contact = Contact(nom_complet=prenom, email=email)
            db.session.add(new_contact)

    db.session.commit()
    return jsonify({"message": "Contacts ajoutés avec succès"}), 201

 

@google_bp.route("/view-contacts", methods=["GET"])
@jwt_required()
def view_contacts():
    current_user = get_jwt_identity()
    user_id = int(current_user["id"]) if isinstance(current_user, dict) else int(current_user)

    contacts = Contact.query.filter_by(utilisateur_id=user_id).all()
    
    contacts_list = [
        {
            "id": c.id,
            "nom_complet": c.nom_complet,
            "email": c.email,
            "numero_tel": c.numero_tel,
            "adresse": c.adresse,
            "organisation": c.organisation
        } for c in contacts
    ]

    return jsonify({"contacts": contacts_list}), 200

@google_bp.route("/add-contact", methods=["POST"])
@jwt_required()
def add_contact():
    current_user = get_jwt_identity()
    user_id = int(current_user["id"]) if isinstance(current_user, dict) else int(current_user)

    data = request.get_json()
    if not data:
        return jsonify({"error": "Données JSON requises"}), 400

    nom_complet = data.get("nom_complet")
    email = data.get("email")
    numero_tel = data.get("numero_tel")
    adresse = data.get("adresse")
    organisation = data.get("organisation")

    if not nom_complet or not email:
        return jsonify({"error": "Le nom complet et l'email sont obligatoires"}), 400

    if Contact.query.filter_by(email=email, utilisateur_id=user_id).first():
        return jsonify({"error": "Ce contact existe déjà"}), 409

    try:
        new_contact = Contact(
            nom_complet=nom_complet,
            email=email,
            numero_tel=numero_tel,
            adresse=adresse,
            organisation=organisation,
            utilisateur_id=user_id  # 🔗 Associer au bon utilisateur
        )
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({"message": "Contact ajouté avec succès"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erreur lors de l'ajout du contact", "details": str(e)}), 500