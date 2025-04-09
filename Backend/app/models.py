from .create_app import db
from datetime import datetime

class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    numero_tel = db.Column(db.String(20))  # Tu peux ajuster la taille si nécessaire
    role = db.Column(db.String(50), nullable=False)
    
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_complet = db.Column(db.String(100))
    email = db.Column(db.String(100))
    numero_tel = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    organisation = db.Column(db.String(50))
    utilisateur_id = db.Column(
        db.Integer, 
        db.ForeignKey("utilisateur.id", ondelete="CASCADE"), 
        nullable=False
    )
    
# Association Many-to-Many pour la liste de diffusion
courrier_utilisateur = db.Table('courrier_utilisateur',
    db.Column('courrier_id', db.Integer, db.ForeignKey('courrier.id'), primary_key=True),
    db.Column('utilisateur_id', db.Integer, db.ForeignKey('utilisateur.id'), primary_key=True)
)

class Courrier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_courrier = db.Column(db.String(50), nullable=False)  # arrivé ou départ 
    priority = db.Column(db.String(50), nullable=False)
    arrival_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    object = db.Column(db.String(255), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)

    # Liste de diffusion finale (utilisateurs sélectionnés dans la partie traitante)
    liste_diffusion = db.relationship('Utilisateur', secondary=courrier_utilisateur, backref='courriers_diffusés')
    
    
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_fichier = db.Column(db.String(255), nullable=False)
    chemin_fichier = db.Column(db.String(255), nullable=False)
    courrier_id = db.Column(db.Integer, db.ForeignKey('courrier.id'), nullable=False)
 
class Workflow(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  courrier_id = db.Column(db.Integer, db.ForeignKey('courrier.id'))
  utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))  # qui est l'étape actuelle (Directeur, Service RH, etc.)
  etape = db.Column(db.String(100))  # Exemple : "Affectation Directeur", "Traitement Service RH", "Validation Secrétaire"
  statut = db.Column(db.String(50))  # Exemple : "en attente", "en cours", "terminé"
  date_debut = db.Column(db.DateTime, default=datetime.utcnow)
  date_fin = db.Column(db.DateTime, nullable=True)

  courrier = db.relationship('Courrier', backref='workflows')
  
  
  
class Notification(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))
  courrier_id = db.Column(db.Integer, db.ForeignKey('courrier.id'))
  message = db.Column(db.String(255))
  statut = db.Column(db.String(50), default='non lu')  # ou "lu"
  date_creation = db.Column(db.DateTime, default=datetime.utcnow)

  utilisateur = db.relationship('Utilisateur', backref='notifications')
  courrier = db.relationship('Courrier', backref='notifications')