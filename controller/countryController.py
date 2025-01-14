from flask import Blueprint, jsonify, request
from connect_db import get_db_connection, DBConnection
import psycopg2.extras

# Créer un Blueprint pour le contrôleur
country_controller = Blueprint('country_controller', __name__)

# Fonction pour récupérer les données des pays depuis la base de données
def fetch_countries():
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM country")
            countries = cursor.fetchall()
            return countries
    except Exception as e:
        print("Erreur lors de la récupération des données des pays :", e)
        return []

# Route GET pour récupérer tous les pays
@country_controller.route('/countries', methods=['GET'])
def get_countries():
    countries = fetch_countries()
    if not countries:
        return jsonify({"error": "No countries found"}), 404
    return jsonify(countries)

# Route GET pour récupérer un pays spécifique par ID
@country_controller.route('/country/<int:country_id>', methods=['GET'])
def get_country(country_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM country WHERE id_country = %s", (country_id,))
            country = cursor.fetchone()
            if not country:
                return jsonify({"error": "Country not found"}), 404
            return jsonify(country)
    except Exception as e:
        print("Erreur lors de la récupération des données du pays :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route POST pour ajouter un nouveau pays
@country_controller.route('/country', methods=['POST'])
def create_country():
    try:
        # Vérification des données envoyées dans la requête
        new_country = request.json

        if "name" not in new_country or "population" not in new_country or "id_climat_type" not in new_country or "id_continent" not in new_country:
            return jsonify({"error": "Missing required fields"}), 400

        name = new_country["name"]
        population = new_country["population"]
        pib = new_country.get("pib")  # PIB est optionnel
        id_climat_type = new_country["id_climat_type"]
        id_continent = new_country["id_continent"]

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO country (name, population, pib, id_climat_type, id_continent)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_country
                """,
                (name, population, pib, id_climat_type, id_continent)
            )
            # L'ID est renvoyé directement par PostgreSQL grâce à RETURNING id_country
            new_country_id = cursor.fetchone()[0]
            conn.commit()

        return jsonify({
            "id_country": new_country_id,  # L'ID généré est renvoyé dans la réponse
            "name": name,
            "population": population,
            "pib": pib,
            "id_climat_type": id_climat_type,
            "id_continent": id_continent
        }), 201

    except Exception as e:
        print("Erreur lors de la création du pays :", e)
        return jsonify({"error": "An error occurred"}), 500


# Route PUT pour modifier un pays existant
@country_controller.route('/country/<int:country_id>', methods=['PUT'])
def update_country(country_id):
    try:
        # Vérification des données envoyées dans la requête
        updated_country = request.json

        if "name" not in updated_country or "population" not in updated_country or "id_climat_type" not in updated_country or "id_continent" not in updated_country:
            return jsonify({"error": "Missing required fields"}), 400

        name = updated_country["name"]
        population = updated_country["population"]
        pib = updated_country.get("pib")  # PIB est optionnel
        id_climat_type = updated_country["id_climat_type"]
        id_continent = updated_country["id_continent"]

        with DBConnection() as conn:
            cursor = conn.cursor()
            # Mettre à jour les données du pays en fonction de l'ID
            cursor.execute(
                """
                UPDATE country
                SET name = %s, population = %s, pib = %s, id_climat_type = %s, id_continent = %s
                WHERE id_country = %s
                RETURNING id_country, name, population, pib, id_climat_type, id_continent
                """,
                (name, population, pib, id_climat_type, id_continent, country_id)
            )
            updated_country_data = cursor.fetchone()
            if not updated_country_data:
                return jsonify({"error": "Country not found"}), 404

            conn.commit()

        return jsonify({
            "id_country": updated_country_data[0],
            "name": updated_country_data[1],
            "population": updated_country_data[2],
            "pib": updated_country_data[3],
            "id_climat_type": updated_country_data[4],
            "id_continent": updated_country_data[5]
        }), 200

    except Exception as e:
        print("Erreur lors de la mise à jour du pays :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route DELETE pour supprimer un pays
@country_controller.route('/country/<int:country_id>', methods=['DELETE'])
def delete_country(country_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            # Supprimer le pays en fonction de l'ID
            cursor.execute("DELETE FROM country WHERE id_country = %s RETURNING id_country", (country_id,))
            deleted_country = cursor.fetchone()

            if not deleted_country:
                return jsonify({"error": "Country not found"}), 404

            conn.commit()

        return jsonify({"message": f"Country with ID {country_id} has been deleted successfully"}), 200

    except Exception as e:
        print("Erreur lors de la suppression du pays :", e)
        return jsonify({"error": "An error occurred"}), 500
