import sqlite3

# Ruta de la base de datos
db_path = "/Users/danielmoyafuster/FonotecaRadioUMH/db/FonotecaRadioUMH.db"

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar si la columna "album_release_date" ya existe en la tabla fonoteca_canciones
cursor.execute("PRAGMA table_info(fonoteca_canciones);")
columns = [col[1] for col in cursor.fetchall()]

# Si la columna no existe, la añadimos
if "album_release_date" not in columns:
    cursor.execute("ALTER TABLE fonoteca_canciones ADD COLUMN album_release_date TEXT;")
    conn.commit()
    print("✔ Se ha añadido la columna 'album_release_date' a la tabla fonoteca_canciones.")
else:
    print("✔ La columna 'album_release_date' ya existe en la tabla fonoteca_canciones.")

# Cerrar conexión
conn.close()