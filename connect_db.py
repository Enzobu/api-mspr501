# connect_db.py

import psycopg2

DATABASE = {
    "host": "enzo-palermo.com",
    "database": "mspr501",
    "user": "mspr501",
    "password": "s5t4v5",
    "port": 5432
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DATABASE)
        print("Connexion réussie à la base de données")
        return conn
    except Exception as e:
        print("Erreur lors de la connexion à la base de données :", e)
        return None

# Gestionnaire de contexte pour une meilleure gestion des connexions
class DBConnection:
    def __enter__(self):
        self.conn = get_db_connection()
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
            print("Connexion fermée")

def test_db_connection():
    try:
        conn = psycopg2.connect(**DATABASE)
        conn.close()  # Ferme la connexion une fois que le test est réussi
        print("Connexion à la base de données réussie.")
    except Exception as e:
        print("Erreur lors de la connexion à la base de données :", e)

test_db_connection()
