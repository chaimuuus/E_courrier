# courrier_bp.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from .models import db, Courrier, Utilisateur, Contact
from flask_jwt_extended import jwt_required, get_jwt_identity

# Création du Blueprint pour le courrier
courrier_bp = Blueprint('courrier', __name__)




## enregisterer couurier == recuperer document mn biblioteteque ate pc drag and drop et complter formulaire et enregisterer et c'est ttout 


## systeme d'archivage et c'est bon 
















# Route pour enregistrer un courrier d'arrivé
@courrier_bp.route('/courrier/arrive', methods=['POST'])
@jwt_required()  # S'assurer que l'utilisateur est authentifié
def enregistrer_courrier_arrive():
    current_user = get_jwt_identity()
    user_id = int(current_user["id"]) if isinstance(current_user, dict) else int(current_user)

    # Récupérer les données du courrier depuis le JSON du body
    data = request.get_json()

    try:
        # Créer un nouvel objet de type Courrier avec les informations fournies
        nouveau_courrier = Courrier(
            type_courrier="arrivé",  # Comme c'est un courrier d'arrivée
            priority=data["priority"],  # Priorité du courrier (ex. 'haute', 'normale')
            arrival_date=datetime.strptime(data["arrival_date"], "%Y-%m-%d %H:%M:%S"),  # Assurez-vous que la date arrive au bon format
            object=data["object"],  # Objet du courrier
            sender_id=data["sender_id"],  # ID de l'expéditeur (contact)
            initiateur_id=user_id,  # ID de l'initiateur (utilisateur actuel)
            destinataire_id=data.get("destinataire_id")  # ID du destinataire, s'il est disponible
        )

        # Ajouter la liste de diffusion, si elle est présente dans la requête
        if "liste_diffusion" in data:
            for utilisateur_id in data["liste_diffusion"]:
                destinataire = Utilisateur.query.get(utilisateur_id)
                if destinataire:
                    nouveau_courrier.liste_diffusion.append(destinataire)

        # Sauvegarder le courrier dans la base de données
        db.session.add(nouveau_courrier)
        db.session.commit()

        return jsonify({"message": "Courrier d'arrivée enregistré avec succès.", "courrier_id": nouveau_courrier.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erreur lors de l'enregistrement du courrier.", "error": str(e)}), 500

# Autres routes pour les courriers peuvent être ajoutées ici...
