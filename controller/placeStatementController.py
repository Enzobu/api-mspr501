from flask import Blueprint, jsonify, request
from connect_db import get_db_connection, DBConnection
import psycopg2.extras

# Créer un Blueprint pour le contrôleur
place_statement_controller = Blueprint('place_statement_controller', __name__)

# Fonction pour récupérer les données des associations place_statement depuis la base de données
def fetch_place_statements():
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM place_statement")
            place_statements = cursor.fetchall()
            return place_statements
    except Exception as e:
        print("Erreur lors de la récupération des données des places_statements :", e)
        return []

# Route GET pour récupérer toutes les associations place_statement
@place_statement_controller.route('/place_statements', methods=['GET'])
def get_place_statements():
    place_statements = fetch_place_statements()
    if not place_statements:
        return jsonify({"error": "No place_statements found"}), 404
    return jsonify(place_statements)

# Route GET pour récupérer une association spécifique par composite key
@place_statement_controller.route('/place_statement', methods=['GET'])
def get_place_statement():
    try:
        id_country = request.args.get('id_country', type=int)
        id_statement = request.args.get('id_statement', type=int)
        id_region = request.args.get('id_region', type=int)
        id_city = request.args.get('id_city', type=int)

        if not all([id_country, id_statement, id_region, id_city]):
            return jsonify({"error": "Missing one or more key parameters"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM place_statement 
                WHERE id_country = %s AND id_statement = %s AND id_region = %s AND id_city = %s
            """, (id_country, id_statement, id_region, id_city))
            place_statement = cursor.fetchone()

            if not place_statement:
                return jsonify({"error": "Place_statement not found"}), 404

            return jsonify(place_statement)

    except Exception as e:
        print("Erreur lors de la récupération des données de place_statement :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route POST pour ajouter une nouvelle association place_statement
@place_statement_controller.route('/place_statement', methods=['POST'])
def create_place_statement():
    try:
        new_place_statement = request.json

        required_fields = ["id_country", "id_statement", "id_region", "id_city"]
        if not all(field in new_place_statement for field in required_fields):
            return jsonify({"error": f"Missing one or more required fields: {required_fields}"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO place_statement (id_country, id_statement, id_region, id_city)
                VALUES (%s, %s, %s, %s)
            """, (
                new_place_statement["id_country"],
                new_place_statement["id_statement"],
                new_place_statement["id_region"],
                new_place_statement["id_city"]
            ))
            conn.commit()

        return jsonify({"message": "Place_statement created successfully"}), 201

    except Exception as e:
        print("Erreur lors de la création de place_statement :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route PUT pour modifier une association existante dans place_statement
@place_statement_controller.route('/place_statement', methods=['PUT'])
def update_place_statement():
    try:
        # Données envoyées dans la requête
        update_data = request.json

        required_fields = ["id_country", "id_statement", "id_region", "id_city"]
        if not all(field in update_data for field in required_fields):
            return jsonify({"error": f"Missing one or more required fields: {required_fields}"}), 400

        # Vérification des nouveaux champs pour mise à jour
        new_values = update_data.get("new_values")
        if not new_values or not isinstance(new_values, dict):
            return jsonify({"error": "Missing or invalid 'new_values' field"}), 400

        # Générer dynamiquement les champs à mettre à jour
        update_fields = []
        update_values = []
        for key, value in new_values.items():
            update_fields.append(f"{key} = %s")
            update_values.append(value)

        if not update_fields:
            return jsonify({"error": "No fields provided for update"}), 400

        # Ajouter les valeurs des clés primaires à la liste des valeurs de mise à jour
        update_values.extend([
            update_data["id_country"],
            update_data["id_statement"],
            update_data["id_region"],
            update_data["id_city"]
        ])

        with DBConnection() as conn:
            cursor = conn.cursor()

            # Construire la requête SQL pour la mise à jour
            cursor.execute(f"""
                UPDATE place_statement
                SET {", ".join(update_fields)}
                WHERE id_country = %s AND id_statement = %s AND id_region = %s AND id_city = %s
                RETURNING id_country, id_statement, id_region, id_city
            """, update_values)

            updated_record = cursor.fetchone()

            if not updated_record:
                return jsonify({"error": "Place_statement not found"}), 404

            conn.commit()

        return jsonify({
            "message": "Place_statement updated successfully",
            "updated_record": {
                "id_country": updated_record[0],
                "id_statement": updated_record[1],
                "id_region": updated_record[2],
                "id_city": updated_record[3]
            }
        }), 200

    except Exception as e:
        print("Erreur lors de la mise à jour de place_statement :", e)
        return jsonify({"error": "An error occurred"}), 500
    
# Route DELETE pour supprimer une association place_statement
@place_statement_controller.route('/place_statement', methods=['DELETE'])
def delete_place_statement():
    try:
        id_country = request.args.get('id_country', type=int)
        id_statement = request.args.get('id_statement', type=int)
        id_region = request.args.get('id_region', type=int)
        id_city = request.args.get('id_city', type=int)

        # Vérification des paramètres obligatoires
        if not all([id_country, id_statement, id_region, id_city]):
            return jsonify({"error": "Missing one or more key parameters"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            # Supprimer l'association en fonction des clés primaires
            cursor.execute("""
                DELETE FROM place_statement 
                WHERE id_country = %s AND id_statement = %s AND id_region = %s AND id_city = %s
                RETURNING id_country, id_statement, id_region, id_city
            """, (id_country, id_statement, id_region, id_city))
            deleted_place_statement = cursor.fetchone()

            if not deleted_place_statement:
                return jsonify({"error": "Place_statement not found"}), 404

            conn.commit()

        return jsonify({
            "message": f"Place_statement with keys ({id_country}, {id_statement}, {id_region}, {id_city}) has been deleted successfully"
        }), 200

    except Exception as e:
        print("Erreur lors de la suppression de place_statement :", e)
        return jsonify({"error": "An error occurred"}), 500
