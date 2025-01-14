from flask import Flask
from connect_db import get_db_connection, DBConnection
from controller import (
    countryController, diseaseController, statementController,
    regionController, cityController, placeStatementController,
    continentController, climatTypeController, weatherReportController
)

app = Flask(__name__)

# Tester la connexion à la base de données au démarrage
db_connection = get_db_connection()

if not db_connection:
    print("Impossible de démarrer l'application sans une connexion à la base de données.")
    exit(1)

@app.route('/example')
def example_route():
    with DBConnection() as conn:
        if not conn:
            return {"error": "Database connection failed"}, 500
        # Exemple de récupération de données ici si nécessaire
        return {"message": "Connexion réussie à la base de données"}, 200

# Liste des Blueprints à enregistrer
blueprints = [
    countryController.country_controller,
    diseaseController.disease_controller,
    statementController.statement_controller,
    regionController.region_controller,
    cityController.city_controller,
    placeStatementController.placeStatement_controller,
    continentController.continent_controller,
    climatTypeController.climat_type_controller,
    weatherReportController.weatherReport_controller
]

# Enregistrer tous les Blueprints
for blueprint in blueprints:
    app.register_blueprint(blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
