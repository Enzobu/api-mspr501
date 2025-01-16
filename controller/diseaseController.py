from flask import Blueprint, jsonify, request
from connect_db import DBConnection
import psycopg2.extras

# Créer un Blueprint pour le contrôleur
disease_controller = Blueprint('disease_controller', __name__)

# Fonction pour récupérer les données des maladies depuis la base de données
def fetch_diseases():
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM disease")
            diseases = cursor.fetchall()
            return diseases
    except Exception as e:
        print("Erreur lors de la récupération des données des maladies :", e)
        return []

# Route GET pour récupérer toutes les maladies
@disease_controller.route('/diseases', methods=['GET'])
def get_diseases():
    diseases = fetch_diseases()
    if not diseases:
        return jsonify({"error": "No diseases found"}), 404
    return jsonify(diseases)

# Route GET pour récupérer une maladie spécifique par ID
@disease_controller.route('/disease/<int:disease_id>', methods=['GET'])
def get_disease(disease_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM disease WHERE id_disease = %s", (disease_id,))
            disease = cursor.fetchone()
            if not disease:
                return jsonify({"error": "Disease not found"}), 404
            return jsonify(disease)
    except Exception as e:
        print("Erreur lors de la récupération des données de la maladie :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route POST pour ajouter une nouvelle maladie
@disease_controller.route('/disease', methods=['POST'])
def create_disease():
    try:
        # Vérification des données envoyées dans la requête
        new_disease = request.json

        if "name" not in new_disease or "is_pandemic" not in new_disease:
            return jsonify({"error": "Missing 'name' or 'is_pandemic'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO disease (name, is_pandemic)
                VALUES (%s, %s) RETURNING id_disease
                """,
                (new_disease["name"], new_disease["is_pandemic"])
            )
            new_disease_id = cursor.fetchone()[0]
            conn.commit()

        return jsonify({
            "id_disease": new_disease_id,
            "name": new_disease["name"],
            "is_pandemic": new_disease["is_pandemic"]
        }), 201

    except Exception as e:
        print("Erreur lors de la création de la maladie :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route PUT pour modifier une maladie existante
@disease_controller.route('/disease/<int:disease_id>', methods=['PUT'])
def update_disease(disease_id):
    try:
        # Vérification des données envoyées dans la requête
        updated_disease = request.json

        if "name" not in updated_disease or "is_pandemic" not in updated_disease:
            return jsonify({"error": "Missing 'name' or 'is_pandemic'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            # Mettre à jour les données de la maladie en fonction de l'ID
            cursor.execute(
                """
                UPDATE disease
                SET name = %s, is_pandemic = %s
                WHERE id_disease = %s
                RETURNING id_disease, name, is_pandemic
                """,
                (
                    updated_disease["name"],
                    updated_disease["is_pandemic"],
                    disease_id
                )
            )
            updated_disease_data = cursor.fetchone()
            if not updated_disease_data:
                return jsonify({"error": "Disease not found"}), 404

            conn.commit()

        return jsonify({
            "id_disease": updated_disease_data[0],
            "name": updated_disease_data[1],
            "is_pandemic": updated_disease_data[2]
        }), 200

    except Exception as e:
        print("Erreur lors de la mise à jour de la maladie :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route DELETE pour supprimer une maladie
@disease_controller.route('/disease/<int:disease_id>', methods=['DELETE'])
def delete_disease(disease_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            # Supprimer la maladie en fonction de l'ID
            cursor.execute("DELETE FROM disease WHERE id_disease = %s RETURNING id_disease", (disease_id,))
            deleted_disease = cursor.fetchone()

            if not deleted_disease:
                return jsonify({"error": "Disease not found"}), 404

            conn.commit()

        return jsonify({"message": f"Disease with ID {disease_id} has been deleted successfully"}), 200

    except Exception as e:
        print("Erreur lors de la suppression de la maladie :", e)
        return jsonify({"error": "An error occurred"}), 500
