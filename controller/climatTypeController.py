from flask import Blueprint, jsonify, request
from connect_db import get_db_connection, DBConnection
import psycopg2.extras

# Créer un Blueprint pour le contrôleur
climat_type_controller = Blueprint('climat_type_controller', __name__)

# Fonction pour récupérer les données des types de climat depuis la base de données
def fetch_climat_types():
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM climat_type")
            climat_types = cursor.fetchall()
            return climat_types
    except Exception as e:
        print("Erreur lors de la récupération des données des types de climat :", e)
        return []

# Route GET pour récupérer tous les types de climat
@climat_type_controller.route('/climat_types', methods=['GET'])
def get_climat_types():
    climat_types = fetch_climat_types()
    if not climat_types:
        return jsonify({"error": "No climat types found"}), 404
    return jsonify(climat_types)

# Route GET pour récupérer un type de climat spécifique par ID
@climat_type_controller.route('/climat_type/<int:climat_type_id>', methods=['GET'])
def get_climat_type(climat_type_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM climat_type WHERE id_climat_type = %s", (climat_type_id,))
            climat_type = cursor.fetchone()
            if not climat_type:
                return jsonify({"error": "Climat type not found"}), 404
            return jsonify(climat_type)
    except Exception as e:
        print("Erreur lors de la récupération des données du type de climat :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route POST pour ajouter un nouveau type de climat
@climat_type_controller.route('/climat_type', methods=['POST'])
def create_climat_type():
    try:
        # Vérification des données envoyées dans la requête
        new_climat_type = request.json

        if "name" not in new_climat_type:
            return jsonify({"error": "Missing 'name'"}), 400

        # Description est optionnelle
        description = new_climat_type.get("description")

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO climat_type (name, description)
                VALUES (%s, %s) RETURNING id_climat_type
                """,
                (new_climat_type["name"], description)
            )
            # L'ID est renvoyé directement par PostgreSQL grâce à RETURNING id_climat_type
            new_climat_type_id = cursor.fetchone()[0]
            conn.commit()

        return jsonify({
            "id_climat_type": new_climat_type_id,  # L'ID généré est renvoyé dans la réponse
            "name": new_climat_type["name"],
            "description": description
        }), 201

    except Exception as e:
        print("Erreur lors de la création du type de climat :", e)
        return jsonify({"error": "An error occurred"}), 500


# Route PUT pour modifier un type de climat existant
@climat_type_controller.route('/climat_type/<int:climat_type_id>', methods=['PUT'])
def update_climat_type(climat_type_id):
    try:
        # Vérification des données envoyées dans la requête
        updated_climat_type = request.json

        if "name" not in updated_climat_type:
            return jsonify({"error": "Missing 'name'"}), 400

        # Description est optionnelle
        description = updated_climat_type.get("description")

        with DBConnection() as conn:
            cursor = conn.cursor()
            # Mettre à jour les données du type de climat en fonction de l'ID
            cursor.execute(
                """
                UPDATE climat_type
                SET name = %s, description = %s
                WHERE id_climat_type = %s
                RETURNING id_climat_type, name, description
                """,
                (
                    updated_climat_type["name"],
                    description,
                    climat_type_id
                )
            )
            updated_climat_type_data = cursor.fetchone()
            if not updated_climat_type_data:
                return jsonify({"error": "Climat type not found"}), 404

            conn.commit()

        return jsonify({
            "id_climat_type": updated_climat_type_data[0],
            "name": updated_climat_type_data[1],
            "description": updated_climat_type_data[2]
        }), 200

    except Exception as e:
        print("Erreur lors de la mise à jour du type de climat :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route DELETE pour supprimer un type de climat
@climat_type_controller.route('/climat_type/<int:climat_type_id>', methods=['DELETE'])
def delete_climat_type(climat_type_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            # Supprimer le type de climat en fonction de l'ID
            cursor.execute("DELETE FROM climat_type WHERE id_climat_type = %s RETURNING id_climat_type", (climat_type_id,))
            deleted_climat_type = cursor.fetchone()

            if not deleted_climat_type:
                return jsonify({"error": "Climat type not found"}), 404

            conn.commit()

        return jsonify({"message": f"Climat type with ID {climat_type_id} has been deleted successfully"}), 200

    except Exception as e:
        print("Erreur lors de la suppression du type de climat :", e)
        return jsonify({"error": "An error occurred"}), 500
