from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

def conectar():
    return sqlite3.connect("database.db")

def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS desplazamientos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estudiante TEXT,
        localidad TEXT,
        tiempo INTEGER,
        transporte TEXT,
        hora_pico TEXT
    )
    """)

    conn.commit()
    conn.close()

crear_tabla()

@app.route("/")
def index():

    conn = conectar()
    cursor = conn.cursor()

    filtro = request.args.get("transporte")

    if filtro:
        cursor.execute("SELECT tiempo FROM desplazamientos WHERE transporte=?", (filtro,))
    else:
        cursor.execute("SELECT tiempo FROM desplazamientos")

    datos = cursor.fetchall()
    conn.close()

    tiempos = [d[0] for d in datos]

    frecuencia = {}
    for t in tiempos:
        frecuencia[t] = frecuencia.get(t, 0) + 1

    total = len(tiempos)

    probabilidades = {}
    for k, v in frecuencia.items():
        probabilidades[k] = v / total if total > 0 else 0

    return render_template(
        "index.html",
        frecuencia=frecuencia,
        probabilidades=probabilidades,
        total=total,
        filtro=filtro
    )

@app.route("/guardar", methods=["POST"])
def guardar():

    estudiante = request.form["estudiante"]
    localidad = request.form["localidad"]
    tiempo = request.form["tiempo"]
    transporte = request.form["transporte"]
    hora_pico = request.form["hora_pico"]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO desplazamientos(estudiante,localidad,tiempo,transporte,hora_pico)
    VALUES(?,?,?,?,?)
    """, (estudiante, localidad, tiempo, transporte, hora_pico))

    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)