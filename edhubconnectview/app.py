from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# Exemple de configuration pour SQLite
DATABASE_URI = 'sqlite:///projet.db'
engine = create_engine(DATABASE_URI)

@app.route('/')
def index():
    # Utiliser Pandas pour effectuer une requête SQL et transformer les résultats en DataFrame
    query_projet = "SELECT * FROM projet;"
    query_cours = "SELECT * FROM cours;"
    query_thematique = "SELECT * FROM thematique;"
    query_ressource = "SELECT * FROM ressource;"
    query_projet_thematique = "SELECT * FROM projet_thematique;"

    df_projet = pd.read_sql_query(query_projet, engine)
    df_cours = pd.read_sql_query(query_cours, engine)
    df_thematique = pd.read_sql_query(query_thematique, engine)
    df_ressource = pd.read_sql_query(query_ressource, engine)
    df_projet_thematique = pd.read_sql_query(query_projet_thematique, engine)

    # ... (autres variables pour les autres tables)

    # Utiliser Flask pour rendre une page HTML avec les représentations HTML des tableaux
    return render_template(
        'index.html',
        df_projet=df_projet,
        df_cours=df_cours,
        df_thematique=df_thematique,
        df_ressource=df_ressource,
        df_projet_thematique=df_projet_thematique
    )

if __name__ == '__main__':
    app.run(debug=False)
