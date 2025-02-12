import sqlite3
import pandas as pd

# Ruta de la base de datos SQLite
db_path = "./db/FonotecaRadioUMH.db"

# Conectar a la base de datos
conn = sqlite3.connect(db_path)

# Ejecutar la consulta SQL
query = """
SELECT COUNT(*) AS total, genero_musical 
FROM fonoteca_cd 
GROUP BY genero_musical;
"""

df = pd.read_sql_query(query, conn)

# Cerrar la conexión a la base de datos
conn.close()

# Guardar el resultado en un archivo Excel
excel_path = "generos_musicales.xlsx"
df.to_excel(excel_path, index=False)

print(f"✔ Archivo Excel guardado en: {excel_path}")