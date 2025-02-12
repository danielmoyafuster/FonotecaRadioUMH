import sqlite3

# Ruta de la base de datos SQLite
db_path = "/Users/danielmoyafuster/FonotecaRadioUMH/db/FonotecaRadioUMH.db"

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar qué columnas existen en la tabla fonoteca_canciones
cursor.execute("PRAGMA table_info(fonoteca_canciones);")
columns = [col[1] for col in cursor.fetchall()]

# Lista de nuevas columnas que queremos agregar
new_columns = {
    "danceability": "REAL",      # Nivel de baile (0-1)
    "energy": "REAL",            # Nivel de energía (0-1)
    "valence": "REAL",           # Nivel de positividad/felicidad (0-1)
    "tempo": "REAL",             # Tempo en BPM
    "instrumentalness": "REAL",  # Si es instrumental (0-1)
    "speechiness": "REAL",       # Cantidad de voz hablada (0-1)
    "acousticness": "REAL"       # Si es acústico (0-1)
}

# Agregar las columnas si no existen
for column, data_type in new_columns.items():
    if column not in columns:
        cursor.execute(f"ALTER TABLE fonoteca_canciones ADD COLUMN {column} {data_type};")
        print(f"✔ Se ha añadido la columna '{column}'.")

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()

print("✔ Todas las columnas necesarias han sido añadidas a la base de datos.")