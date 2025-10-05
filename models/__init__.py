from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Auditoire(db.Model):
    __tablename__ = 'auditoire'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    capacite = db.Column(db.Integer, nullable=True)

class Enseignant(db.Model):
    __tablename__ = 'enseignant'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    postnom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(50), nullable=False)

class Etudiant(db.Model):
    __tablename__ = 'etudiant'
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(50), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    postnom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(10), nullable=False)
    auditoire_id = db.Column(db.Integer, db.ForeignKey('auditoire.id'), nullable=False)
    
    # Changement du nom de la backref pour éviter le conflit
    auditoire = db.relationship('Auditoire', backref='etudiants_list')
    
    def generer_matricule(self):
        """Génère un matricule automatique basé sur l'année et l'ID"""
        annee = datetime.now().year
        return f"ISC{annee}{self.id:04d}"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Le matricule sera généré après l'insertion en base

class Cours(db.Model):
    __tablename__ = 'cours'
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(200), nullable=False)  # Nom du cours
    auditoire_id = db.Column(db.Integer, db.ForeignKey('auditoire.id'), nullable=False)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignant.id'), nullable=False)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    volume_horaire = db.Column(db.Integer, nullable=False)

    auditoire = db.relationship('Auditoire', backref='cours_list')
    enseignant = db.relationship('Enseignant', backref='cours')    
class Presence(db.Model):
    __tablename__ = 'presence'
    id = db.Column(db.Integer, primary_key=True)
    cours_id = db.Column(db.Integer, db.ForeignKey('cours.id'), nullable=False)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiant.id'), nullable=False)
    date_jour = db.Column(db.Date, nullable=False)
    present = db.Column(db.Boolean, default=False)
    cumule_presence = db.Column(db.Integer, default=0)

    cours = db.relationship('Cours', backref='presences')
    etudiant = db.relationship('Etudiant', backref='presences')

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='admin')