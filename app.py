from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, Auditoire, Enseignant, Etudiant, Cours, Presence,User
from datetime import datetime,date 
import hashlib 
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Changez cette clé

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///horaire_isc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    # Recréer toutes les tables
    db.drop_all()
    db.create_all()
    
    # Créer l'utilisateur admin
    admin_user = User(username='admin', password='password', role='admin')
    db.session.add(admin_user)
    
    # Créer les auditoires selon la structure académique
    auditoires = [
        # Licence 1
        Auditoire(nom='L1 Informatique de Gestion', capacite=60),
        Auditoire(nom='L1 Douane et Accise', capacite=55),
        Auditoire(nom='L1 Comptabilité', capacite=65),
        Auditoire(nom='L1 Marketing', capacite=50),
        
        # Licence 2
        Auditoire(nom='L2 Informatique de Gestion', capacite=60),
        Auditoire(nom='L2 Douane et Accise', capacite=55),
        Auditoire(nom='L2 Comptabilité', capacite=65),
        Auditoire(nom='L2 Marketing', capacite=50),
        
        # Licence 3
        Auditoire(nom='L3 Informatique de Gestion', capacite=60),
        Auditoire(nom='L3 Douane et Accise', capacite=55),
        Auditoire(nom='L3 Comptabilité', capacite=65),
        Auditoire(nom='L3 Marketing', capacite=50),
        
        # Master 1
        Auditoire(nom='M1 Conception', capacite=40),
        Auditoire(nom='M1 Réseau', capacite=40),
        Auditoire(nom='M1 Douane et Accise', capacite=45),
        Auditoire(nom='M1 Comptabilité', capacite=45),
        Auditoire(nom='M1 Marketing', capacite=40),
        
        # Master 2
        Auditoire(nom='M2 Conception', capacite=35),
        Auditoire(nom='M2 Réseau', capacite=35),
        Auditoire(nom='M2 Douane et Accise', capacite=40),
        Auditoire(nom='M2 Comptabilité', capacite=40),
        Auditoire(nom='M2 Marketing', capacite=35),
    ]
    
    for auditoire in auditoires:
        db.session.add(auditoire)
    
    db.session.commit()

    # Créer les enseignants
    enseignants = [
        # Professeurs pour Informatique
        Enseignant(nom='MUKENGE', postnom='KABONGO', prenom='Didier', grade='Professeur'),
        Enseignant(nom='KALUME', postnom='MUSANGU', prenom='Pascal', grade='Professeur'),
        Enseignant(nom='TSHIBANGU', postnom='MBAYO', prenom='Gloria', grade='Chef de travaux'),
        
        # Professeurs pour Douane et Accise
        Enseignant(nom='KASONGO', postnom='ILUNGA', prenom='Marc', grade='Professeur'),
        Enseignant(nom='LUBELO', postnom='MUTOMBO', prenom='Julie', grade='Chef de travaux'),
        
        # Professeurs pour Comptabilité
        Enseignant(nom='KABEYA', postnom='MWAMBA', prenom='David', grade='Professeur'),
        Enseignant(nom='MULONDA', postnom='KABANGE', prenom='Sarah', grade='Chef de travaux'),
        
        # Professeurs pour Marketing
        Enseignant(nom='MUBENGA', postnom='KATEMBO', prenom='Rachel', grade='Professeur'),
        Enseignant(nom='KAPENDA', postnom='LUBOYA', prenom='Eric', grade='Chef de travaux'),
        
        # Assistants
        Enseignant(nom='MUSAU', postnom='KABUYA', prenom='Patrick', grade='Assistant'),
        Enseignant(nom='KABUYA', postnom='MUSAU', prenom='Annie', grade='Assistant'),
    ]
    
    for enseignant in enseignants:
        db.session.add(enseignant)
    
    db.session.commit()

    # Données pour générer des étudiants réalistes
    noms = ['KABILA', 'TSHISEKEDI', 'LUMUMBA', 'MOBUTU', 'KASAVUBU', 'TSHOMBE', 'KABANGE', 'MWAMBA', 'KATEMBO', 'MUBENGA']
    postnoms = ['MUKENGE', 'KABONGO', 'MUSANGU', 'ILUNGA', 'LUBELO', 'MWAMBA', 'KABEYA', 'MULONDA', 'KAPENDA', 'MUSAU']
    prenoms_m = ['David', 'Patrick', 'Marc', 'Eric', 'Pascal', 'Didier', 'Jacques', 'Christian', 'Jonathan', 'Steve']
    prenoms_f = ['Sarah', 'Julie', 'Rachel', 'Annie', 'Gloria', 'Micheline', 'Esther', 'Dorcas', 'Ruth', 'Naomie']

    # Créer 10 étudiants pour chaque auditoire
    print("Création des étudiants...")
    for auditoire_id in range(1, len(auditoires) + 1):
        for i in range(10):  # 10 étudiants par auditoire
            if i < 5:  # 5 masculins
                genre = 'M'
                prenom = prenoms_m[i % len(prenoms_m)]
            else:  # 5 féminins
                genre = 'F'
                prenom = prenoms_f[i % len(prenoms_f)]
            
            nom = noms[i % len(noms)]
            postnom = postnoms[(i + 2) % len(postnoms)]
            
            etudiant = Etudiant(
                nom=nom,
                postnom=postnom,
                prenom=prenom,
                genre=genre,
                auditoire_id=auditoire_id,
                matricule="TEMPORAIRE"
            )
            db.session.add(etudiant)
            db.session.flush()
            etudiant.matricule = etudiant.generer_matricule()
    
    db.session.commit()

    # Créer au moins 3 cours pour chaque auditoire
    print("Création des cours...")
    from datetime import date, timedelta
    
    # Noms de cours par domaine
    cours_informatique = [
        'Algorithmique et Programmation',
        'Base de Données',
        'Réseaux Informatiques',
        'Développement Web',
        'Systèmes d\'Exploitation'
    ]
    
    cours_douane = [
        'Droit Douanier',
        'Procédures Douanières',
        'Fiscalité Internationale',
        'Contrôle des Marchandises',
        'Logistique Douanière'
    ]
    
    cours_comptabilite = [
        'Comptabilité Générale',
        'Analyse Financière',
        'Fiscalité des Entreprises',
        'Contrôle de Gestion',
        'Audit Comptable'
    ]
    
    cours_marketing = [
        'Marketing Fondamental',
        'Études de Marché',
        'Communication Marketing',
        'Marketing Digital',
        'Stratégie Commerciale'
    ]
    
    cours_conception = [
        'Conception Logicielle',
        'Architecture des Systèmes',
        'UML et Modélisation',
        'Design Patterns',
        'Ingénierie des Besoins'
    ]
    
    cours_reseau = [
        'Réseaux Avancés',
        'Sécurité Réseau',
        'Administration Systèmes',
        'Cloud Computing',
        'Virtualisation'
    ]

    # Assigner des cours selon l'auditoire
    for auditoire in auditoires:
        nom_auditoire = auditoire.nom
        cours_disponibles = []
        
        if 'Informatique de Gestion' in nom_auditoire:
            cours_disponibles = cours_informatique
            enseignant_ids = [1, 2, 3]  # Enseignants en informatique
        elif 'Douane et Accise' in nom_auditoire:
            cours_disponibles = cours_douane
            enseignant_ids = [4, 5]  # Enseignants en douane
        elif 'Comptabilité' in nom_auditoire:
            cours_disponibles = cours_comptabilite
            enseignant_ids = [6, 7]  # Enseignants en comptabilité
        elif 'Marketing' in nom_auditoire:
            cours_disponibles = cours_marketing
            enseignant_ids = [8, 9]  # Enseignants en marketing
        elif 'Conception' in nom_auditoire:
            cours_disponibles = cours_conception
            enseignant_ids = [1, 2, 3]  # Enseignants en informatique
        elif 'Réseau' in nom_auditoire:
            cours_disponibles = cours_reseau
            enseignant_ids = [1, 2, 3]  # Enseignants en informatique
        
        # Créer 3 cours pour cet auditoire
        for i in range(3):
            if i < len(cours_disponibles):
                designation = cours_disponibles[i]  # Utiliser le nom du cours comme désignation
                enseignant_id = enseignant_ids[i % len(enseignant_ids)]
                
                cours = Cours(
                    designation=designation,  # AJOUT DE LA DÉSIGNATION
                    auditoire_id=auditoire.id,
                    enseignant_id=enseignant_id,
                    date_debut=date.today() + timedelta(days=i*30),
                    date_fin=date.today() + timedelta(days=(i+1)*30),
                    volume_horaire=45 if 'Master' in nom_auditoire else 60
                )
                db.session.add(cours)
    
    # Final commit
    db.session.commit()
    
    print("Initialisation terminée avec succès!")
    print(f"✅ {len(auditoires)} auditoires créés")
    print(f"✅ {Enseignant.query.count()} enseignants créés")
    print(f"✅ {Etudiant.query.count()} étudiants créés")
    print(f"✅ {Cours.query.count()} cours créés")
# Routes pour les présences

@app.route('/presence', methods=['GET', 'POST'])  # Ajout de 'POST'
def presence():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    # Si c'est une requête POST (enregistrement des présences)
    if request.method == 'POST':
        cours_id = request.form['cours_id']
        date_jour = request.form['date_jour']
        
        try:
            date_jour = datetime.strptime(date_jour, '%Y-%m-%d').date()
            
            # Mettre à jour les présences
            for key, value in request.form.items():
                if key.startswith('presence_'):
                    etudiant_id = key.split('_')[1]
                    presence = Presence.query.filter_by(
                        cours_id=cours_id,
                        etudiant_id=etudiant_id,
                        date_jour=date_jour
                    ).first()
                    
                    if presence:
                        presence.present = (value == 'on')
            
            db.session.commit()
            flash('Présences enregistrées avec succès!', 'success')
            
        except ValueError:
            flash('Format de date invalide!', 'danger')
        
        return redirect(url_for('presence', cours_id=cours_id, date_jour=date_jour.isoformat()))
    
    # Si c'est une requête GET (affichage normal)
    # Récupérer les cours pour le filtre
    cours_list = Cours.query.all()
    
    # Récupérer les paramètres de filtre
    cours_id = request.args.get('cours_id')
    date_jour = request.args.get('date_jour', date.today().isoformat())
    
    presences = []
    cours_selected = None
    
    if cours_id and date_jour:
        try:
            date_jour = datetime.strptime(date_jour, '%Y-%m-%d').date()
            cours_selected = Cours.query.get(cours_id)
            
            if cours_selected:
                # Récupérer les étudiants de l'auditoire du cours
                etudiants_auditoire = Etudiant.query.filter_by(auditoire_id=cours_selected.auditoire_id).all()
                
                for etudiant in etudiants_auditoire:
                    presence = Presence.query.filter_by(
                        cours_id=cours_id,
                        etudiant_id=etudiant.id,
                        date_jour=date_jour
                    ).first()
                    
                    if not presence:
                        # Créer un nouvel enregistrement de présence
                        presence = Presence(
                            cours_id=cours_id,
                            etudiant_id=etudiant.id,
                            date_jour=date_jour,
                            present=False
                        )
                        db.session.add(presence)
                
                db.session.commit()
                
                # Récupérer toutes les présences pour ce cours et cette date
                presences = Presence.query.filter_by(
                    cours_id=cours_id,
                    date_jour=date_jour
                ).all()
                
        except ValueError:
            flash('Format de date invalide!', 'danger')
    
    return render_template('presence.html',
                         cours_list=cours_list,
                         cours_selected=cours_selected,
                         presences=presences,
                         date_jour=date_jour)
@app.route('/presence/marquer', methods=['POST'])
def marquer_presence():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    cours_id = request.form['cours_id']
    date_jour = request.form['date_jour']
    
    try:
        date_jour = datetime.strptime(date_jour, '%Y-%m-%d').date()
        
        # Mettre à jour les présences
        for key, value in request.form.items():
            if key.startswith('presence_'):
                etudiant_id = key.split('_')[1]
                presence = Presence.query.filter_by(
                    cours_id=cours_id,
                    etudiant_id=etudiant_id,
                    date_jour=date_jour
                ).first()
                
                if presence:
                    presence.present = (value == 'on')
        
        db.session.commit()
        flash('Présences enregistrées avec succès!', 'success')
        
    except ValueError:
        flash('Format de date invalide!', 'danger')
    
    return redirect(url_for('presence', cours_id=cours_id, date_jour=date_jour.isoformat()))
@app.route('/presence/rapport')
def rapport_presence():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    cours_id = request.args.get('cours_id')
    etudiant_id = request.args.get('etudiant_id')
    
    cours_list = Cours.query.all()
    etudiants = Etudiant.query.all()
    
    rapports = []
    cours_selected = None
    etudiant_selected = None
    
    if cours_id:
        cours_selected = Cours.query.get(cours_id)
        
        # Calculer le rapport de présence par étudiant pour ce cours
        if cours_selected:
            # Récupérer les étudiants de l'auditoire du cours (au lieu de tous les étudiants)
            etudiants_auditoire = Etudiant.query.filter_by(auditoire_id=cours_selected.auditoire_id).all()
            
            for etudiant in etudiants_auditoire:
                # Compter le nombre total de séances pour ce cours
                total_seances = Presence.query.filter_by(
                    cours_id=cours_id,
                    etudiant_id=etudiant.id
                ).count()
                
                # Compter le nombre de présences
                presences_count = Presence.query.filter_by(
                    cours_id=cours_id,
                    etudiant_id=etudiant.id,
                    present=True
                ).count()
                
                # Calculer le pourcentage
                pourcentage = (presences_count / total_seances * 100) if total_seances > 0 else 0
                
                rapports.append({
                    'etudiant': etudiant,
                    'total_seances': total_seances,
                    'presences_count': presences_count,
                    'pourcentage': round(pourcentage, 2)
                })
    
    return render_template('rapport_presence.html',
                         cours_list=cours_list,
                         etudiants=etudiants,
                         rapports=rapports,
                         cours_selected=cours_selected,
                         etudiant_selected=etudiant_selected)


# Routes pour les cours
@app.route('/cours')
def cours():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    cours_list = Cours.query.all()
    auditoires_list = Auditoire.query.all()
    enseignants_list = Enseignant.query.all()
    
    # Ajouter les propriétés calculées pour chaque cours
    today = date.today()
    for cours in cours_list:
        # Calculer la durée en jours
        duree = (cours.date_fin - cours.date_debut).days
        cours.duree = duree
        
        # Déterminer le statut
        if today < cours.date_debut:
            cours.statut = 'a_venir'
        elif today > cours.date_fin:
            cours.statut = 'termine'
        else:
            cours.statut = 'en_cours'
    
    return render_template('cours.html', 
                         cours_list=cours_list,
                         auditoires_list=auditoires_list,
                         enseignants_list=enseignants_list)

@app.route('/cours/ajouter', methods=['GET', 'POST'])
def ajouter_cours():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        designation = request.form['designation']  # Nouveau champ
        auditoire_id = request.form['auditoire_id']
        enseignant_id = request.form['enseignant_id']
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin']
        volume_horaire = request.form['volume_horaire']
        
        # Conversion des dates
        try:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
        except ValueError:
            flash('Format de date invalide!', 'danger')
            return redirect(url_for('ajouter_cours'))
        
        # Vérifier si la date de fin est après la date de début
        if date_fin < date_debut:
            flash('La date de fin doit être après la date de début!', 'danger')
            return redirect(url_for('ajouter_cours'))
        
        nouveau_cours = Cours(
            designation=designation,  # Ajout de la désignation
            auditoire_id=auditoire_id,
            enseignant_id=enseignant_id,
            date_debut=date_debut,
            date_fin=date_fin,
            volume_horaire=volume_horaire
        )
        
        db.session.add(nouveau_cours)
        db.session.commit()
        
        flash('Cours ajouté avec succès!')
        return redirect(url_for('cours'))
    
    # Récupérer les auditoires et enseignants pour les select
    auditoires = Auditoire.query.all()
    enseignants = Enseignant.query.all()
    
    return render_template('ajouter_cours.html', 
                         auditoires=auditoires, 
                         enseignants=enseignants)

@app.route('/cours/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_cours(id):
    if 'username' not in session:
        return redirect(url_for('home'))
    
    cours = Cours.query.get_or_404(id)
    
    if request.method == 'POST':
        designation = request.form['designation']  # Nouveau champ
        auditoire_id = request.form['auditoire_id']
        enseignant_id = request.form['enseignant_id']
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin']
        volume_horaire = request.form['volume_horaire']
        
        # Conversion des dates
        try:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
        except ValueError:
            flash('Format de date invalide!', 'danger')
            return redirect(url_for('modifier_cours', id=id))
        
        # Vérifier si la date de fin est après la date de début
        if date_fin < date_debut:
            flash('La date de fin doit être après la date de début!', 'danger')
            return redirect(url_for('modifier_cours', id=id))
        
        cours.designation = designation  # Mise à jour de la désignation
        cours.auditoire_id = auditoire_id
        cours.enseignant_id = enseignant_id
        cours.date_debut = date_debut
        cours.date_fin = date_fin
        cours.volume_horaire = volume_horaire
        
        db.session.commit()
        flash('Cours modifié avec succès!')
        return redirect(url_for('cours'))
    
    auditoires = Auditoire.query.all()
    enseignants = Enseignant.query.all()
    
    return render_template('modifier_cours.html', 
                         cours=cours, 
                         auditoires=auditoires, 
                         enseignants=enseignants)

@app.route('/cours/supprimer/<int:id>')
def supprimer_cours(id):
    if 'username' not in session:
        return redirect(url_for('home'))
    
    cours = Cours.query.get_or_404(id)
    
    # Vérifier si le cours a des présences associées
    if cours.presences:
        flash('Impossible de supprimer ce cours car il a des présences associées!', 'danger')
        return redirect(url_for('cours'))
    
    db.session.delete(cours)
    db.session.commit()
    
    flash('Cours supprimé avec succès!')
    return redirect(url_for('cours'))
# Routes pour les étudiants
@app.route('/etudiants')
def etudiants():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    # Récupérer le filtre auditoire s'il existe
    auditoire_id = request.args.get('auditoire_id')
    
    if auditoire_id:
        etudiants = Etudiant.query.filter_by(auditoire_id=auditoire_id).all()
    else:
        etudiants = Etudiant.query.all()
    
    auditoires_count = Auditoire.query.count()
    auditoires_list = Auditoire.query.all()
    
    return render_template('etudiants.html', 
                         etudiants=etudiants, 
                         auditoires_count=auditoires_count,
                         auditoires_list=auditoires_list)
@app.route('/ajouter_etudiant', methods=['GET', 'POST'])
def ajouter_etudiant():
    if 'username' not in session:
        nom = request.form['nom']
        postnom = request.form['postnom']
        prenom = request.form['prenom']
        genre = request.form['genre']
        auditoire_id = request.form['auditoire_id']
        
        nouvel_etudiant = Etudiant(
            nom=nom, 
            postnom=postnom, 
            prenom=prenom, 
            auditoire_id=auditoire_id,
            matricule="TEMPORAIRE"  # Valeur temporaire
        )
        
        db.session.add(nouvel_etudiant)
        db.session.flush()  # Pour obtenir l'ID sans commit
        
        # Générer le matricule avec l'ID
        nouvel_etudiant.matricule = nouvel_etudiant.generer_matricule()
        
    
    # Récupérer la liste des auditoires pour le formulaire
    auditoires = Auditoire.query.all()
    return render_template('ajouter_etudiant.html', auditoires=auditoires)
@app.route('/etudiants/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_etudiant(id):
    if 'username' not in session:
        return redirect(url_for('home'))
    
    etudiant = Etudiant.query.get_or_404(id)
    etudiant.postnom = request.form['postnom']
    etudiant.prenom = request.form['prenom']
    etudiant.auditoire_id = request.form['auditoire_id']
        
    db.session.commit()
    flash('Étudiant modifié avec succès!')
    return redirect(url_for('etudiants'))
    
    # Récupérer la liste des auditoires pour le formulaire
    auditoires = Auditoire.query.all()
    return render_template('modifier_etudiant.html', etudiant=etudiant, auditoires=auditoires)

@app.route('/etudiants/supprimer/<int:id>')
def supprimer_etudiant(id):
    if 'username' not in session:
        return redirect(url_for('home'))
    
    etudiant = Etudiant.query.get_or_404(id)
    
    # Vérifier si l'étudiant a des présences associées
    if etudiant.presences:
        flash('Impossible de supprimer cet étudiant car il a des présences associées!', 'danger')
        return redirect(url_for('etudiants'))
    
    db.session.delete(etudiant)
    db.session.commit()
    
    flash('Étudiant supprimé avec succès!')
    return redirect(url_for('etudiants'))

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['username'] = username
        session['role'] = user.role
        return redirect(url_for('accueil'))  # Redirection vers la page d'accueil
    flash('Mot de passe incorrect, veuillez réessayer.')
    return redirect(url_for('home'))



@app.route('/accueil')
def accueil():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('accueil.html', username=session['username'], role=session['role'])

# Routes pour les auditoires
@app.route('/auditoires')
def auditoires():
    if 'username' not in session:
        return redirect(url_for('home'))
    auditoires = Auditoire.query.all()
    return render_template('auditoires.html', auditoires=auditoires)

@app.route('/auditoires/ajouter', methods=['GET', 'POST'])
def ajouter_auditoire():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        nom = request.form['nom']
        capacite = request.form['capacite']
        
        nouvel_auditoire = Auditoire(nom=nom, capacite=capacite)
        db.session.add(nouvel_auditoire)
        db.session.commit()
        
        flash('Auditoire ajouté avec succès!')
        return redirect(url_for('auditoires'))
    
    return render_template('ajouter_auditoire.html')

@app.route('/auditoires/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_auditoire(id):
    if 'username' not in session:
        return redirect(url_for('home'))
    
    auditoire = Auditoire.query.get_or_404(id)
    
    if request.method == 'POST':
        auditoire.nom = request.form['nom']
        auditoire.capacite = request.form['capacite']
        
        db.session.commit()
        flash('Auditoire modifié avec succès!')
        return redirect(url_for('auditoires'))
    
    return render_template('modifier_auditoire.html', auditoire=auditoire)

@app.route('/auditoires/supprimer/<int:id>')
def supprimer_auditoire(id):
    if 'username' not in session:
        return redirect(url_for('home'))
    
    auditoire = Auditoire.query.get_or_404(id)
    db.session.delete(auditoire)
    db.session.commit()
    
    flash('Auditoire supprimé avec succès!')
    return redirect(url_for('auditoires'))

# Routes pour les enseignants
@app.route('/enseignants')
def enseignants():
    if 'username' not in session:
        return redirect(url_for('home'))
    enseignants = Enseignant.query.all()
    return render_template('enseignants.html', enseignants=enseignants)

@app.route('/enseignants/ajouter', methods=['GET', 'POST'])
def ajouter_enseignant():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        nom = request.form['nom']
        postnom = request.form['postnom']
        prenom = request.form['prenom']
        grade = request.form['grade']
        
        nouvel_enseignant = Enseignant(
            nom=nom, 
            postnom=postnom, 
            prenom=prenom, 
            grade=grade
        )
        db.session.add(nouvel_enseignant)
        db.session.commit()
        
        flash('Enseignant ajouté avec succès!')
        return redirect(url_for('enseignants'))
    
    return render_template('ajouter_enseignant.html')

@app.route('/enseignants/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_enseignant(id):
    if 'username' not in session:
        return redirect(url_for('home'))
    
    enseignant = Enseignant.query.get_or_404(id)
    
    if request.method == 'POST':
        enseignant.nom = request.form['nom']
        enseignant.postnom = request.form['postnom']
        enseignant.prenom = request.form['prenom']
        enseignant.grade = request.form['grade']
        
        db.session.commit()
        flash('Enseignant modifié avec succès!')
        return redirect(url_for('enseignants'))
    
    return render_template('modifier_enseignant.html', enseignant=enseignant)

@app.route('/enseignants/supprimer/<int:id>')
def supprimer_enseignant(id):
    if 'username' not in session:
        return redirect(url_for('home'))
    
    enseignant = Enseignant.query.get_or_404(id)
    
    # Vérifier si l'enseignant a des cours associés
    if enseignant.cours:
        flash('Impossible de supprimer cet enseignant car il a des cours associés!', 'danger')
        return redirect(url_for('enseignants'))
    
    db.session.delete(enseignant)
    db.session.commit()
    
    flash('Enseignant supprimé avec succès!')
    return redirect(url_for('enseignants'))

# Routes pour la gestion des utilisateurs (admin seulement)
@app.route('/utilisateurs')
def utilisateurs():
    if 'username' not in session or session.get('role') != 'admin':
        flash('Accès non autorisé!', 'danger')
        return redirect(url_for('accueil'))
    
    utilisateurs = User.query.all()
    return render_template('utilisateurs.html', utilisateurs=utilisateurs)

@app.route('/utilisateurs/ajouter', methods=['GET', 'POST'])
def ajouter_utilisateur():
    if 'username' not in session or session.get('role') != 'admin':
        flash('Accès non autorisé!', 'danger')
        return redirect(url_for('accueil'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur existe déjà!', 'danger')
            return render_template('ajouter_utilisateur.html')
        
        nouvel_utilisateur = User(
            username=username,
            password=password,
            role=role
        )
        
        db.session.add(nouvel_utilisateur)
        db.session.commit()
        
        flash('Utilisateur ajouté avec succès!', 'success')
        return redirect(url_for('utilisateurs'))
    
    return render_template('ajouter_utilisateur.html')

@app.route('/utilisateurs/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_utilisateur(id):
    if 'username' not in session or session.get('role') != 'admin':
        flash('Accès non autorisé!', 'danger')
        return redirect(url_for('accueil'))
    
    utilisateur = User.query.get_or_404(id)
    
    # Empêcher la modification de l'admin principal
    if utilisateur.username == 'admin' and session['username'] != 'admin':
        flash('Vous ne pouvez pas modifier l\'administrateur principal!', 'danger')
        return redirect(url_for('utilisateurs'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        # Vérifier si le username existe déjà pour un autre utilisateur
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != utilisateur.id:
            flash('Ce nom d\'utilisateur existe déjà!', 'danger')
            return render_template('modifier_utilisateur.html', utilisateur=utilisateur)
        
        utilisateur.username = username
        if password:  # Ne mettre à jour le mot de passe que si fourni
            utilisateur.password = password
        utilisateur.role = role
        
        db.session.commit()
        flash('Utilisateur modifié avec succès!', 'success')
        return redirect(url_for('utilisateurs'))
    
    return render_template('modifier_utilisateur.html', utilisateur=utilisateur)

@app.route('/utilisateurs/supprimer/<int:id>')
def supprimer_utilisateur(id):
    if 'username' not in session or session.get('role') != 'admin':
        flash('Accès non autorisé!', 'danger')
        return redirect(url_for('accueil'))
    
    utilisateur = User.query.get_or_404(id)
    
    # Empêcher la suppression de l'admin principal et de soi-même
    if utilisateur.username == 'admin':
        flash('Impossible de supprimer l\'administrateur principal!', 'danger')
        return redirect(url_for('utilisateurs'))
    
    if utilisateur.username == session['username']:
        flash('Vous ne pouvez pas supprimer votre propre compte!', 'danger')
        return redirect(url_for('utilisateurs'))
    
    db.session.delete(utilisateur)
    db.session.commit()
    
    flash('Utilisateur supprimé avec succès!', 'success')
    return redirect(url_for('utilisateurs'))

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    utilisateur = User.query.filter_by(username=session['username']).first()
    
    if not utilisateur:
        flash('Utilisateur non trouvé!', 'danger')
        return redirect(url_for('accueil'))
    
    if request.method == 'POST':
        ancien_password = request.form['ancien_password']
        nouveau_password = request.form['nouveau_password']
        confirmer_password = request.form['confirmer_password']
        
        # Vérifier l'ancien mot de passe
        if ancien_password != utilisateur.password:
            flash('Ancien mot de passe incorrect!', 'danger')
            return redirect(url_for('profil'))
        
        # Vérifier la confirmation du nouveau mot de passe
        if nouveau_password != confirmer_password:
            flash('Les nouveaux mots de passe ne correspondent pas!', 'danger')
            return redirect(url_for('profil'))
        
        # Mettre à jour le mot de passe
        utilisateur.password = nouveau_password
        db.session.commit()
        
        flash('Mot de passe modifié avec succès!', 'success')
        return redirect(url_for('profil'))
    
    return render_template('profil.html', utilisateur=utilisateur)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)