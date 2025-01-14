from flask import Blueprint, jsonify, request
from connect_db import get_db_connection, DBConnection
import psycopg2.extras

# Créer un Blueprint pour le contrôleur
city_controller = Blueprint('city_controller', __name__)

# Fonction pour récupérer les données des villes depuis la base de données
def fetch_cities():
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM city")
            cities = cursor.fetchall()
            return cities
    except Exception as e:
        print("Erreur lors de la récupération des données des villes :", e)
        return []

# Route GET pour récupérer toutes les villes
@city_controller.route('/cities', methods=['GET'])
def get_cities():
    cities = fetch_cities()
    if not cities:
        return jsonify({"error": "No cities found"}), 404
    return jsonify(cities)

# Route GET pour récupérer une ville spécifique par ID
@city_controller.route('/city/<int:city_id>', methods=['GET'])
def get_city(city_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM city WHERE id_city = %s", (city_id,))
            city = cursor.fetchone()
            if not city:
                return jsonify({"error": "City not found"}), 404
            return jsonify(city)
    except Exception as e:
        print("Erreur lors de la récupération des données de la ville :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route POST pour ajouter une nouvelle ville
@city_controller.route('/city', methods=['POST'])
def create_city():
    try:
        # Vérification des données envoyées dans la requête
        new_city = request.json

        if "latitude" not in new_city or "longitude" not in new_city or "name" not in new_city:
            return jsonify({"error": "Missing 'latitude', 'longitude' or 'name'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO city (latitude, longitude, name, population)
                VALUES (%s, %s, %s, %s) RETURNING id_city
                """,
                (new_city["latitude"], new_city["longitude"], new_city["name"], new_city.get("population"))
            )
            # L'ID est renvoyé directement par PostgreSQL grâce à RETURNING id_city
            new_city_id = cursor.fetchone()[0]
            conn.commit()

        return jsonify({
            "id_city": new_city_id,
            "latitude": new_city["latitude"],
            "longitude": new_city["longitude"],
            "name": new_city["name"],
            "population": new_city.get("population", None)
        }), 201

    except Exception as e:
        print("Erreur lors de la création de la ville :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route PUT pour modifier une ville existante
@city_controller.route('/city/<int:city_id>', methods=['PUT'])
def update_city(city_id):
    try:
        # Vérification des données envoyées dans la requête
        updated_city = request.json

        if "latitude" not in updated_city or "longitude" not in updated_city or "name" not in updated_city:
            return jsonify({"error": "Missing 'latitude', 'longitude' or 'name'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            # Mettre à jour les données de la ville en fonction de l'ID
            cursor.execute(
                """
                UPDATE city
                SET latitude = %s, longitude = %s, name = %s, population = %s
                WHERE id_city = %s
                RETURNING id_city, latitude, longitude, name, population
                """,
                (
                    updated_city["latitude"],
                    updated_city["longitude"],
                    updated_city["name"],
                    updated_city.get("population"),
                    city_id
                )
            )
            updated_city_data = cursor.fetchone()
            if not updated_city_data:
                return jsonify({"error": "City not found"}), 404

            conn.commit()

        return jsonify({
            "id_city": updated_city_data[0],
            "latitude": updated_city_data[1],
            "longitude": updated_city_data[2],
            "name": updated_city_data[3],
            "population": updated_city_data[4]
        }), 200

    except Exception as e:
        print("Erreur lors de la mise à jour de la ville :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route DELETE pour supprimer une ville
@city_controller.route('/city/<int:id_city>', methods=['DELETE'])
def delete_city(id_city):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            # Supprimer la ville en fonction de l'ID
            cursor.execute("DELETE FROM city WHERE id_city = %s RETURNING id_city", (id_city,))
            deleted_city = cursor.fetchone()

            if not deleted_city:
                return jsonify({"error": "City not found"}), 404

            conn.commit()

        return jsonify({"message": f"City with ID {id_city} has been deleted successfully"}), 200

    except Exception as e:
        print("Erreur lors de la suppression de la ville :", e)
        return jsonify({"error": "An error occurred"}), 500
