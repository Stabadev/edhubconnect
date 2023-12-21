from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projet.db'
app.config['SECRET_KEY'] = '12345678' 
db = SQLAlchemy(app)



# Modèle pour les projets
class Projet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_projet = db.Column(db.String(255), nullable=False)
    numero_projet = db.Column(db.String(50), nullable=False)
    thematiques = db.relationship('Thematique', secondary='projet_thematique', back_populates='projets')

    cours = db.relationship('Cours', backref='projet', lazy=True)
    ressources = db.relationship('Ressource', backref='projet', lazy=True)
    duree_totale = db.Column(db.Integer, default=0)  # Champ pour la durée totale du projet

# Modèle pour les thématiques
class Thematique(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_thematique = db.Column(db.String(50), nullable=False, unique=True)
    projets = db.relationship('Projet', secondary='projet_thematique', back_populates='thematiques')

# Table de liaison entre les projets et les thématiques
projet_thematique = db.Table('projet_thematique',
    db.Column('projet_id', db.Integer, db.ForeignKey('projet.id'), primary_key=True),
    db.Column('thematique_id', db.Integer, db.ForeignKey('thematique.id'), primary_key=True)
)

# Modèle pour les cours
class Cours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_cours = db.Column(db.String(255), nullable=False)
    lien_cours = db.Column(db.String(255), nullable=False)
    duree_cours = db.Column(db.Integer, nullable=False)
    difficulte_cours = db.Column(db.String(20), nullable=False)
    projet_id = db.Column(db.Integer, db.ForeignKey('projet.id'), nullable=False)

# Modèle pour les ressources
class Ressource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lien_ressource = db.Column(db.String(255), nullable=False)
    commentaire_ressource = db.Column(db.Text)
    projet_id = db.Column(db.Integer, db.ForeignKey('projet.id'), nullable=False)


my_admin = Admin(app, name='MyAdmin', template_mode='bootstrap3')
my_admin.add_view(ModelView(Projet, db.session))
my_admin.add_view(ModelView(Thematique, db.session))


@app.route('/supprimer_cours/<int:cours_id>', methods=['POST'])
def supprimer_cours(cours_id):
    cours = Cours.query.get_or_404(cours_id)
    db.session.delete(cours)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/supprimer_ressource/<int:ressource_id>', methods=['POST'])
def supprimer_ressource(ressource_id):
    # Récupérer la ressource à partir de la base de données
    ressource = Ressource.query.get_or_404(ressource_id)

    # Supprimer la ressource de la base de données
    db.session.delete(ressource)
    db.session.commit()

    # Rediriger vers la page d'index après la suppression
    return redirect(url_for('index'))

@app.route('/admin')
def admin_panel():
    return redirect(url_for('admin.index'))


@app.route('/')
def index():
    projets = Projet.query.all()
    return render_template('index.html', projets=projets)

@app.route('/ajouter_projet', methods=['GET', 'POST'])
def ajouter_projet():
    if request.method == 'POST':
        nom_projet = request.form['nom_projet']
        numero_projet = request.form['numero_projet']
        duree_totale = int(request.form['duree_totale'])  # Récupérer la durée totale depuis le formulaire
        thematiques = request.form.getlist('thematiques')  # Utilisez getlist ici

        nouveau_projet = Projet(nom_projet=nom_projet, numero_projet=numero_projet)

        for nom_thematique in thematiques:
            thematique = Thematique.query.filter_by(nom_thematique=nom_thematique).first()
            print(thematique)  # Vérifiez dans la console serveur si les thématiques sont correctement récupérées
            if thematique:
                nouveau_projet.thematiques.append(thematique)


        nouveau_projet.duree_totale = duree_totale  # Mettez à jour le champ duree_totale

        db.session.add(nouveau_projet)
        db.session.commit()

        return redirect(url_for('index'))

    thematiques = Thematique.query.all()
    return render_template('ajouter_projet.html', thematiques=thematiques)

@app.route('/ajouter_cours/<int:projet_id>', methods=['GET', 'POST'])
def ajouter_cours(projet_id):
    projet = Projet.query.get_or_404(projet_id)

    if request.method == 'POST':
        nom_cours = request.form['nom_cours']
        lien_cours = request.form['lien_cours']
        duree_cours = int(request.form['duree_cours'])
        difficulte_cours = request.form['difficulte_cours']

        nouveau_cours = Cours(nom_cours=nom_cours, lien_cours=lien_cours, duree_cours=duree_cours, difficulte_cours=difficulte_cours, projet=projet)

        db.session.add(nouveau_cours)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('ajouter_cours.html', projet=projet)

@app.route('/ajouter_ressource/<int:projet_id>', methods=['GET', 'POST'])
def ajouter_ressource(projet_id):
    projet = Projet.query.get_or_404(projet_id)

    if request.method == 'POST':
        lien_ressource = request.form['lien_ressource']
        commentaire_ressource = request.form['commentaire_ressource']

        nouvelle_ressource = Ressource(lien_ressource=lien_ressource, commentaire_ressource=commentaire_ressource, projet=projet)

        db.session.add(nouvelle_ressource)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('ajouter_ressource.html', projet=projet)


@app.route('/supprimer_projet/<int:projet_id>', methods=['GET', 'POST'])
def supprimer_projet(projet_id):
    projet = Projet.query.get_or_404(projet_id)

    if request.method == 'POST':
        # Supprimer le projet de la base de données
        db.session.delete(projet)
        db.session.commit()

        flash('Le projet a été supprimé avec succès.', 'success')  # Optionnel : afficher un message de succès

        return redirect(url_for('index'))

    return render_template('supprimer_projet.html', projet=projet)


if __name__ == "__main__":
    # Création des tables dans la base de données
    with app.app_context():
        db.create_all()

    app.run(debug=False, port=5001)
    
    exit()