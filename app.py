import os

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from mysql.connector import Error

load_dotenv()

app = Flask(__name__)

frontend_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500",
    ).split(",")
    if origin.strip()
]
CORS(app, resources={r"/api/*": {"origins": frontend_origins}})

UPSERT_LOADS_SQL = """
INSERT INTO page_load_counter (id, total_loads)
VALUES (1, %s)
ON DUPLICATE KEY UPDATE total_loads = total_loads + %s
"""


def get_database_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


@app.post("/api/loads")
def record_loads():
    payload = request.get_json(silent=True)
    loads = payload.get("loads") if isinstance(payload, dict) else None
    if isinstance(loads, bool) or not isinstance(loads, int) or loads <= 0:
        return jsonify(error="'loads' must be a positive integer"), 400

    connection = None
    cursor = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute(UPSERT_LOADS_SQL, (loads, loads))
        cursor.execute("SELECT total_loads FROM page_load_counter WHERE id = 1")
        row = cursor.fetchone()
        connection.commit()
        if row is None:
            app.logger.error("The page-load counter row is missing after an update")
            return jsonify(error="Unable to read the page-load total"), 500
        return jsonify(total_loads=int(row[0]))
    except Error:
        app.logger.exception("Unable to save page loads to MySQL")
        if connection is not None:
            try:
                connection.rollback()
            except Error:
                app.logger.exception("Unable to roll back the MySQL transaction")
        return jsonify(error="Unable to save page loads"), 503
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    app.run()
