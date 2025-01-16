from flask import Blueprint, jsonify, request
from connect_db import get_db_connection, DBConnection
import psycopg2.extras

# Créer un Blueprint pour le contrôleur
statement_controller = Blueprint('statement_controller', __name__)

# Fonction pour récupérer les données des statements depuis la base de données
def fetch_statements():
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM statement")
            statements = cursor.fetchall()
            return statements
    except Exception as e:
        print("Erreur lors de la récupération des données des statements :", e)
        return []

# Route GET pour récupérer tous les statements
@statement_controller.route('/statements', methods=['GET'])
def get_statements():
    statements = fetch_statements()
    if not statements:
        return jsonify({"error": "No statements found"}), 404
    return jsonify(statements)

# Route GET pour récupérer un statement spécifique par ID
@statement_controller.route('/statement/<int:statement_id>', methods=['GET'])
def get_statement(statement_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM statement WHERE id_statement = %s", (statement_id,))
            statement = cursor.fetchone()
            if not statement:
                return jsonify({"error": "Statement not found"}), 404
            return jsonify(statement)
    except Exception as e:
        print("Erreur lors de la récupération des données du statement :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route POST pour ajouter un nouveau statement
@statement_controller.route('/statement', methods=['POST'])
def create_statement():
    try:
        # Vérification des données envoyées dans la requête
        new_statement = request.json

        # Vérification des champs nécessaires
        required_fields = ["_date", "confirmed", "deaths", "recovered", "active", "new_deaths", "new_cases", "new_recovered", "id_disease"]
        for field in required_fields:
            if field not in new_statement:
                return jsonify({"error": f"Missing '{field}'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO statement (_date, confirmed, deaths, recovered, active, total_tests, new_deaths, new_cases, new_recovered, id_disease)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_statement
                """,
                (
                    new_statement["_date"],
                    new_statement["confirmed"],
                    new_statement["deaths"],
                    new_statement["recovered"],
                    new_statement["active"],
                    new_statement.get("total_tests"),
                    new_statement["new_deaths"],
                    new_statement["new_cases"],
                    new_statement["new_recovered"],
                    new_statement["id_disease"]
                )
            )
            # L'ID est renvoyé directement par PostgreSQL grâce à RETURNING id_statement
            new_statement_id = cursor.fetchone()[0]
            conn.commit()

        return jsonify({
            "id_statement": new_statement_id,
            "_date": new_statement["_date"],
            "confirmed": new_statement["confirmed"],
            "deaths": new_statement["deaths"],
            "recovered": new_statement["recovered"],
            "active": new_statement["active"],
            "total_tests": new_statement.get("total_tests"),
            "new_deaths": new_statement["new_deaths"],
            "new_cases": new_statement["new_cases"],
            "new_recovered": new_statement["new_recovered"],
            "id_disease": new_statement["id_disease"]
        }), 201

    except Exception as e:
        print("Erreur lors de la création du statement :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route PUT pour modifier un statement existant
@statement_controller.route('/statement/<int:statement_id>', methods=['PUT'])
def update_statement(statement_id):
    try:
        # Vérification des données envoyées dans la requête
        updated_statement = request.json

        # Vérification des champs nécessaires
        required_fields = ["_date", "confirmed", "deaths", "recovered", "active", "new_deaths", "new_cases", "new_recovered", "id_disease"]
        for field in required_fields:
            if field not in updated_statement:
                return jsonify({"error": f"Missing '{field}'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            # Mettre à jour les données du statement en fonction de l'ID
            cursor.execute(
                """
                UPDATE statement
                SET _date = %s, confirmed = %s, deaths = %s, recovered = %s, active = %s, total_tests = %s,
                    new_deaths = %s, new_cases = %s, new_recovered = %s, id_disease = %s
                WHERE id_statement = %s
                RETURNING id_statement, _date, confirmed, deaths, recovered, active, total_tests, new_deaths, new_cases, new_recovered, id_disease
                """,
                (
                    updated_statement["_date"],
                    updated_statement["confirmed"],
                    updated_statement["deaths"],
                    updated_statement["recovered"],
                    updated_statement["active"],
                    updated_statement.get("total_tests"),
                    updated_statement["new_deaths"],
                    updated_statement["new_cases"],
                    updated_statement["new_recovered"],
                    updated_statement["id_disease"],
                    statement_id
                )
            )
            updated_statement_data = cursor.fetchone()
            if not updated_statement_data:
                return jsonify({"error": "Statement not found"}), 404

            conn.commit()

        return jsonify({
            "id_statement": updated_statement_data[0],
            "_date": updated_statement_data[1],
            "confirmed": updated_statement_data[2],
            "deaths": updated_statement_data[3],
            "recovered": updated_statement_data[4],
            "active": updated_statement_data[5],
            "total_tests": updated_statement_data[6],
            "new_deaths": updated_statement_data[7],
            "new_cases": updated_statement_data[8],
            "new_recovered": updated_statement_data[9],
            "id_disease": updated_statement_data[10]
        }), 200

    except Exception as e:
        print("Erreur lors de la mise à jour du statement :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route DELETE pour supprimer un statement
@statement_controller.route('/statement/<int:statement_id>', methods=['DELETE'])
def delete_statement(statement_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            # Supprimer le statement en fonction de l'ID
            cursor.execute("DELETE FROM statement WHERE id_statement = %s RETURNING id_statement", (statement_id,))
            deleted_statement = cursor.fetchone()

            if not deleted_statement:
                return jsonify({"error": "Statement not found"}), 404

            conn.commit()

        return jsonify({"message": f"Statement with ID {statement_id} has been deleted successfully"}), 200

    except Exception as e:
        print("Erreur lors de la suppression du statement :", e)
        return jsonify({"error": "An error occurred"}), 500
