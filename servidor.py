"""
PFO 2 - Sistema de Gestión de Tareas
API REST con Flask + SQLite + contraseñas hasheadas (werkzeug).

Endpoints:
    POST /registro  -> {"usuario": "nombre", "contraseña": "1234"}
    POST /login     -> {"usuario": "nombre", "contraseña": "1234"}
    GET  /tareas    -> HTML de bienvenida (requiere sesión iniciada)
"""
import os
import sqlite3

from flask import Flask, jsonify, request, session
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash

DB_NAME = "tareas.db"

app = Flask(__name__)
# Clave para firmar la cookie de sesión. En producción, definirla por variable de entorno.
app.secret_key = os.environ.get("SECRET_KEY", "clave-de-desarrollo-cambiar")


# ---------------------------------------------------------------- Base de datos
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
            """
        )


def leer_credenciales():
    """Devuelve (usuario, contraseña) del JSON recibido, o (None, None) si faltan."""
    datos = request.get_json(silent=True) or {}
    usuario = str(datos.get("usuario", "")).strip()
    password = str(datos.get("contraseña", ""))
    if not usuario or not password:
        return None, None
    return usuario, password


# ------------------------------------------------------------------- Endpoints
@app.route("/registro", methods=["POST"])
def registro():
    usuario, password = leer_credenciales()
    if usuario is None:
        return jsonify({"error": "Se requieren 'usuario' y 'contraseña'"}), 400

    password_hash = generate_password_hash(password)  # salt + hash (nunca texto plano)
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)",
                (usuario, password_hash),
            )
    except sqlite3.IntegrityError:
        return jsonify({"error": "El usuario ya existe"}), 409

    return jsonify({"mensaje": f"Usuario '{usuario}' registrado correctamente"}), 201


@app.route("/login", methods=["POST"])
def login():
    usuario, password = leer_credenciales()
    if usuario is None:
        return jsonify({"error": "Se requieren 'usuario' y 'contraseña'"}), 400

    with get_db() as conn:
        fila = conn.execute(
            "SELECT * FROM usuarios WHERE usuario = ?", (usuario,)
        ).fetchone()

    if fila is None or not check_password_hash(fila["password_hash"], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    session["usuario"] = fila["usuario"]
    return jsonify({"mensaje": f"Bienvenido, {usuario}. Ya podés acceder a /tareas"}), 200


@app.route("/tareas", methods=["GET"])
def tareas():
    if "usuario" not in session:
        return jsonify({"error": "Debés iniciar sesión en /login"}), 401

    usuario = escape(session["usuario"])  # evita inyección de HTML (XSS)
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Gestor de Tareas</title>
        <style>
            body {{ font-family: Arial, sans-serif; background:#f4f6f8;
                   display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }}
            .card {{ background:#fff; padding:2rem 3rem; border-radius:12px;
                    box-shadow:0 4px 12px rgba(0,0,0,.1); text-align:center; }}
            h1 {{ color:#2c3e50; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>¡Bienvenido, {usuario}!</h1>
            <p>Este es tu Sistema de Gestión de Tareas.</p>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
