from flask import Blueprint, jsonify, request
from connect_db import get_db_connection, DBConnection
import psycopg2.extras

# Créer un Blueprint pour le contrôleur
continent_controller = Blueprint('continent_controller', __name__)

# Fonction pour récupérer les données des continents depuis la base de données
def fetch_continents():
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM continent")
            continents = cursor.fetchall()
            return continents
    except Exception as e:
        print("Erreur lors de la récupération des données des continents :", e)
        return []

# Route GET pour récupérer tous les continents
@continent_controller.route('/continents', methods=['GET'])
def get_continents():
    continents = fetch_continents()
    if not continents:
        return jsonify({"error": "No continents found"}), 404
    return jsonify(continents)

# Route GET pour récupérer un continent spécifique par ID
@continent_controller.route('/continent/<int:continent_id>', methods=['GET'])
def get_continent(continent_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM continent WHERE id_continent = %s", (continent_id,))
            continent = cursor.fetchone()
            if not continent:
                return jsonify({"error": "Continent not found"}), 404
            return jsonify(continent)
    except Exception as e:
        print("Erreur lors de la récupération des données du continent :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route POST pour ajouter un nouveau continent
@continent_controller.route('/continent', methods=['POST'])
def create_continent():
    try:
        # Vérification des données envoyées dans la requête
        new_continent = request.json

        if "name" not in new_continent:
            return jsonify({"error": "Missing 'name'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO continent (name)
                VALUES (%s) RETURNING id_continent
                """,
                (new_continent["name"],)
            )
            # L'ID est renvoyé directement par PostgreSQL grâce à RETURNING id_continent
            new_continent_id = cursor.fetchone()[0]
            conn.commit()

        return jsonify({
            "id_continent": new_continent_id,  # L'ID généré est renvoyé dans la réponse
            "name": new_continent["name"]
        }), 201

    except Exception as e:
        print("Erreur lors de la création du continent :", e)
        return jsonify({"error": "An error occurred"}), 500


# Route PUT pour modifier un continent existant
@continent_controller.route('/continent/<int:continent_id>', methods=['PUT'])
def update_continent(continent_id):
    try:
        # Vérification des données envoyées dans la requête
        updated_continent = request.json

        if "name" not in updated_continent:
            return jsonify({"error": "Missing 'name'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            # Mettre à jour les données du continent en fonction de l'ID
            cursor.execute(
                """
                UPDATE continent
                SET name = %s
                WHERE id_continent = %s
                RETURNING id_continent, name
                """,
                (
                    updated_continent["name"],
                    continent_id
                )
            )
            updated_continent_data = cursor.fetchone()
            if not updated_continent_data:
                return jsonify({"error": "Continent not found"}), 404

            conn.commit()

        return jsonify({
            "id_continent": updated_continent_data[0],
            "name": updated_continent_data[1]
        }), 200

    except Exception as e:
        print("Erreur lors de la mise à jour du continent :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route DELETE pour supprimer un continent
@continent_controller.route('/continent/<int:continent_id>', methods=['DELETE'])
def delete_continent(continent_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            # Supprimer le continent en fonction de l'ID
            cursor.execute("DELETE FROM continent WHERE id_continent = %s RETURNING id_continent", (continent_id,))
            deleted_continent = cursor.fetchone()

            if not deleted_continent:
                return jsonify({"error": "Continent not found"}), 404

            conn.commit()

        return jsonify({"message": f"Continent with ID {continent_id} has been deleted successfully"}), 200

    except Exception as e:
        print("Erreur lors de la suppression du continent :", e)
        return jsonify({"error": "An error occurred"}), 500
