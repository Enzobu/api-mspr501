"""
Application Flask pour gérer les données sanitaires et météorologiques.

Cette application fournit des points d'API pour la gestion des données sanitaires (comme les maladies) 
et des données météorologiques (comme le climat et les régions). Elle se connecte à une base de données 
et expose plusieurs routes via l'API Flask-RESTX.

Fonctionnalités principales :
- Connexion à la base de données.
- Documentation de l'API via Swagger.
- Points de terminaison pour les entités sanitaires et météorologiques.
"""

import sys
from flask import Flask         # type: ignore
from flask_restx import Api     # type: ignore
from controller import climat_type_controller, continent_controller, country_climat_type_controller
from controller import country_controller, disease_controller, region_controller, statement_controller
from connect_db import get_db_connection, DBConnection


app = Flask(__name__)

api = Api(app,
          title="MSPR 501 API",
          version="1.0",
          description="Documentation de l'API pour la gestion des données sanitaires et météorologiques.")

api.add_namespace(climat_type_controller.climat_type_namespace, path='/swagger')
api.add_namespace(continent_controller.continent_namespace, path='/swagger')
api.add_namespace(country_controller.country_namespace, path='/swagger')
api.add_namespace(country_climat_type_controller.country_climat_type_namespace, path='/swagger')
api.add_namespace(disease_controller.disease_namespace, path='/swagger')
api.add_namespace(region_controller.region_namespace, path='/swagger')
api.add_namespace(statement_controller.statement_namespace, path='/swagger')

db_connection = get_db_connection()

if not db_connection:
    # Cette condition vérifie si une connexion à la base de données a réussi avant de démarrer l'application.
    # Si la connexion échoue, l'application s'arrête avec un message d'erreur.
    print("Impossible de démarrer l'application sans une connexion à la base de données.")
    sys.exit(1)

@app.route('/status')
def example_route():
    """
    Route de test pour vérifier l'état de la connexion à la base de données.

    Utilise le gestionnaire de connexion DBConnection pour vérifier si la connexion à la base de
    données est active.

    Returns:
        dict: Un message JSON avec l'état de la connexion à la base de données.
    """
    with DBConnection() as conn:
        if not conn:
            return {"error": "Database connection failed"}, 500
        return {"message": "Connexion réussie à la base de données"}, 200

blueprints = [
    climat_type_controller.climat_type_controller,
    continent_controller.continent_controller,
    country_controller.country_controller,
    country_climat_type_controller.country_climat_type_controller,
    disease_controller.disease_controller,
    region_controller.region_controller,
    statement_controller.statement_controller,
]

for blueprint in blueprints:
    # Enregistre les blueprints pour chaque controller de l'API.
    # Les blueprints permettent d'organiser les routes de l'API par fonctionnalité.
    # Parameters:
    #     blueprint (Blueprint): Un blueprint de l'API pour un module spécifique.
    app.register_blueprint(blueprint, url_prefix='/api')

if __name__ == '__main__':
    # Démarre l'application Flask en mode débogage.
    app.run(host='0.0.0.0', port=5000, debug=True)
