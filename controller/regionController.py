from flask import Blueprint, jsonify, request
from connect_db import get_db_connection, DBConnection
import psycopg2.extras

# Créer un Blueprint pour le contrôleur
region_controller = Blueprint('region_controller', __name__)

# Fonction pour récupérer les données des régions depuis la base de données
def fetch_regions():
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM region")
            regions = cursor.fetchall()
            return regions
    except Exception as e:
        print("Erreur lors de la récupération des données des régions :", e)
        return []

# Route GET pour récupérer toutes les régions
@region_controller.route('/regions', methods=['GET'])
def get_regions():
    regions = fetch_regions()
    if not regions:
        return jsonify({"error": "No regions found"}), 404
    return jsonify(regions)

# Route GET pour récupérer une région spécifique par ID
@region_controller.route('/region/<int:region_id>', methods=['GET'])
def get_region(region_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM region WHERE id_region = %s", (region_id,))
            region = cursor.fetchone()
            if not region:
                return jsonify({"error": "Region not found"}), 404
            return jsonify(region)
    except Exception as e:
        print("Erreur lors de la récupération des données de la région :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route POST pour ajouter une nouvelle région
@region_controller.route('/region', methods=['POST'])
def create_region():
    try:
        # Vérification des données envoyées dans la requête
        new_region = request.json

        if "name" not in new_region:
            return jsonify({"error": "Missing 'name'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO region (name, population)
                VALUES (%s, %s) RETURNING id_region
                """,
                (new_region["name"], new_region.get("population"))
            )
            # L'ID est renvoyé directement par PostgreSQL grâce à RETURNING id_region
            new_region_id = cursor.fetchone()[0]
            conn.commit()

        return jsonify({
            "id_region": new_region_id,
            "name": new_region["name"],
            "population": new_region.get("population", None)
        }), 201

    except Exception as e:
        print("Erreur lors de la création de la région :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route PUT pour modifier une région existante
@region_controller.route('/region/<int:region_id>', methods=['PUT'])
def update_region(region_id):
    try:
        # Vérification des données envoyées dans la requête
        updated_region = request.json

        if "name" not in updated_region:
            return jsonify({"error": "Missing 'name'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            # Mettre à jour les données de la région en fonction de l'ID
            cursor.execute(
                """
                UPDATE region
                SET name = %s, population = %s
                WHERE id_region = %s
                RETURNING id_region, name, population
                """,
                (
                    updated_region["name"],
                    updated_region.get("population"),
                    region_id
                )
            )
            updated_region_data = cursor.fetchone()
            if not updated_region_data:
                return jsonify({"error": "Region not found"}), 404

            conn.commit()

        return jsonify({
            "id_region": updated_region_data[0],
            "name": updated_region_data[1],
            "population": updated_region_data[2]
        }), 200

    except Exception as e:
        print("Erreur lors de la mise à jour de la région :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route DELETE pour supprimer une région
@region_controller.route('/region/<int:region_id>', methods=['DELETE'])
def delete_region(region_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            # Supprimer la région en fonction de l'ID
            cursor.execute("DELETE FROM region WHERE id_region = %s RETURNING id_region", (region_id,))
            deleted_region = cursor.fetchone()

            if not deleted_region:
                return jsonify({"error": "Region not found"}), 404

            conn.commit()

        return jsonify({"message": f"Region with ID {region_id} has been deleted successfully"}), 200

    except Exception as e:
        print("Erreur lors de la suppression de la région :", e)
        return jsonify({"error": "An error occurred"}), 500
