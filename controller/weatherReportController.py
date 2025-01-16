from flask import Blueprint, jsonify, request
from connect_db import get_db_connection, DBConnection
import psycopg2.extras

# Créer un Blueprint pour le contrôleur
weather_report_controller = Blueprint('weather_report_controller', __name__)

# Fonction pour récupérer les données des weather reports depuis la base de données
def fetch_weather_reports():
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM weather_report")
            weather_reports = cursor.fetchall()
            return weather_reports
    except Exception as e:
        print("Erreur lors de la récupération des données des weather reports :", e)
        return []

# Route GET pour récupérer tous les weather reports
@weather_report_controller.route('/weather_reports', methods=['GET'])
def get_weather_reports():
    weather_reports = fetch_weather_reports()
    if not weather_reports:
        return jsonify({"error": "No weather reports found"}), 404
    return jsonify(weather_reports)

# Route GET pour récupérer un weather report spécifique par ID
@weather_report_controller.route('/weather_report/<int:report_id>', methods=['GET'])
def get_weather_report(report_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT * FROM weather_report WHERE id_weather_report = %s", (report_id,))
            weather_report = cursor.fetchone()
            if not weather_report:
                return jsonify({"error": "Weather report not found"}), 404
            return jsonify(weather_report)
    except Exception as e:
        print("Erreur lors de la récupération des données du weather report :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route POST pour ajouter un nouveau weather report
@weather_report_controller.route('/weather_report', methods=['POST'])
def create_weather_report():
    try:
        # Vérification des données envoyées dans la requête
        new_weather_report = request.json

        if "date_start" not in new_weather_report or "date_end" not in new_weather_report or "id_country" not in new_weather_report:
            return jsonify({"error": "Missing 'date_start', 'date_end' or 'id_country'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO weather_report (date_start, date_end, average_temperature, average_wind_velocity, humidity_level, id_country)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_weather_report
                """,
                (
                    new_weather_report["date_start"],
                    new_weather_report["date_end"],
                    new_weather_report.get("average_temperature"),
                    new_weather_report.get("average_wind_velocity"),
                    new_weather_report.get("humidity_level"),
                    new_weather_report["id_country"]
                )
            )
            # L'ID est renvoyé directement par PostgreSQL grâce à RETURNING id_weather_report
            new_weather_report_id = cursor.fetchone()[0]
            conn.commit()

        return jsonify({
            "id_weather_report": new_weather_report_id,
            "date_start": new_weather_report["date_start"],
            "date_end": new_weather_report["date_end"],
            "average_temperature": new_weather_report.get("average_temperature"),
            "average_wind_velocity": new_weather_report.get("average_wind_velocity"),
            "humidity_level": new_weather_report.get("humidity_level"),
            "id_country": new_weather_report["id_country"]
        }), 201

    except Exception as e:
        print("Erreur lors de la création du weather report :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route PUT pour modifier un weather report existant
@weather_report_controller.route('/weather_report/<int:report_id>', methods=['PUT'])
def update_weather_report(report_id):
    try:
        # Vérification des données envoyées dans la requête
        updated_weather_report = request.json

        if "date_start" not in updated_weather_report or "date_end" not in updated_weather_report or "id_country" not in updated_weather_report:
            return jsonify({"error": "Missing 'date_start', 'date_end' or 'id_country'"}), 400

        with DBConnection() as conn:
            cursor = conn.cursor()
            # Mettre à jour les données du weather report en fonction de l'ID
            cursor.execute(
                """
                UPDATE weather_report
                SET date_start = %s, date_end = %s, average_temperature = %s, average_wind_velocity = %s, humidity_level = %s, id_country = %s
                WHERE id_weather_report = %s
                RETURNING id_weather_report, date_start, date_end, average_temperature, average_wind_velocity, humidity_level, id_country
                """,
                (
                    updated_weather_report["date_start"],
                    updated_weather_report["date_end"],
                    updated_weather_report.get("average_temperature"),
                    updated_weather_report.get("average_wind_velocity"),
                    updated_weather_report.get("humidity_level"),
                    updated_weather_report["id_country"],
                    report_id
                )
            )
            updated_weather_report_data = cursor.fetchone()
            if not updated_weather_report_data:
                return jsonify({"error": "Weather report not found"}), 404

            conn.commit()

        return jsonify({
            "id_weather_report": updated_weather_report_data[0],
            "date_start": updated_weather_report_data[1],
            "date_end": updated_weather_report_data[2],
            "average_temperature": updated_weather_report_data[3],
            "average_wind_velocity": updated_weather_report_data[4],
            "humidity_level": updated_weather_report_data[5],
            "id_country": updated_weather_report_data[6]
        }), 200

    except Exception as e:
        print("Erreur lors de la mise à jour du weather report :", e)
        return jsonify({"error": "An error occurred"}), 500

# Route DELETE pour supprimer un weather report
@weather_report_controller.route('/weather_report/<int:report_id>', methods=['DELETE'])
def delete_weather_report(report_id):
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            # Supprimer le weather report en fonction de l'ID
            cursor.execute("DELETE FROM weather_report WHERE id_weather_report = %s RETURNING id_weather_report", (report_id,))
            deleted_weather_report = cursor.fetchone()

            if not deleted_weather_report:
                return jsonify({"error": "Weather report not found"}), 404

            conn.commit()

        return jsonify({"message": f"Weather report with ID {report_id} has been deleted successfully"}), 200

    except Exception as e:
        print("Erreur lors de la suppression du weather report :", e)
        return jsonify({"error": "An error occurred"}), 500