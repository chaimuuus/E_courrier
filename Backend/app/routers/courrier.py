from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from ..models import db, Courrier, Utilisateur,Document,Notification
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

# Initialisation du Blueprint
courrier_bp = Blueprint('courrier', __name__)

from werkzeug.utils import secure_filename
import os
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, JWTManager
)
 
UPLOAD_FOLDER = '/path/to/upload/folder'  # Répertoire où tu veux enregistrer les fichiers

# Vérifie si le type de fichier est autorisé
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@courrier_bp.route('/save_courrier', methods=['POST'])
@jwt_required()
def save_courrier():
    data = request.form
    
    # Récupération des informations du formulaire
    type_courrier = data.get('type_courrier')
    priority = data.get('priority')
    object = data.get('object')
    sender_id = data.get('sender_id')
    diffusion_ids = request.form.getlist('diffusion_ids')  # Liste des utilisateurs sélectionnés
    
    # Vérification de la présence des champs nécessaires
    if not type_courrier or not priority or not object or not sender_id:
        return jsonify({"message": "Tous les champs sont requis"}), 400

    # Création du courrier
    courrier = Courrier(
        type_courrier=type_courrier,
        priority=priority,
        object=object,
        sender_id=sender_id  # Assignation de l'expéditeur
    )
    db.session.add(courrier)
    db.session.commit()  # Sauvegarde du courrier

    # Ajout des utilisateurs dans la liste de diffusion
    for user_id in diffusion_ids:
        user = Utilisateur.query.get(user_id)
        if user:
            courrier.liste_diffusion.append(user)

    db.session.commit()  # Sauvegarde des modifications du courrier

    # Envoi de notifications aux utilisateurs de la liste de diffusion
    for user_id in diffusion_ids:
        user = Utilisateur.query.get(user_id)
        if user:
            notification = Notification(
                utilisateur_id=user.id,
                courrier_id=courrier.id,
                message=f"Vous avez reçu un nouveau courrier : {object}",
                statut="non lu"
            )
            db.session.add(notification)

    # Traitement du fichier (si un fichier est inclus)
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "Aucun fichier sélectionné"}), 400

        if file and allowed_file(file.filename):
            # Sécuriser le nom du fichier et le sauvegarder
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # Enregistrer le document dans la base de données et lier au courrier
            document = Document(
                nom_fichier=filename,
                chemin_fichier=file_path,
                courrier_id=courrier.id
            )
            db.session.add(document)
            db.session.commit()

            # Ajouter une notification pour le document
            for user_id in diffusion_ids:
                user = Utilisateur.query.get(user_id)
                if user:
                    notification = Notification(
                        utilisateur_id=user.id,
                        courrier_id=courrier.id,
                        message=f"Un document a été ajouté au courrier : {object}",
                        statut="non lu"
                    )
                    db.session.add(notification)

            db.session.commit()  # Sauvegarde des notifications liées au document

    # Retour de succès avec l'ID du courrier et le document si disponible
    response = {"message": "Courrier enregistré et envoyé aux utilisateurs sélectionnés", "courrier_id": courrier.id}

    if 'file' in request.files:
        response["document_id"] = document.id  # Si un document est téléchargé, inclure son ID

    return jsonify(response), 201
