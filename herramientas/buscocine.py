import sqlite3
import pandas as pd

# Ruta de la base de datos SQLite
db_path = "/Users/danielmoyafuster/FonotecaRadioUMH/db/FonotecaRadioUMH.db"

# Conectar a la base de datos SQLite
conn = sqlite3.connect(db_path)

# Consulta SQL para buscar CDs relacionados con cine
query_cds = """
SELECT id, numero_cd, autor, titulo_cd, genero_musical 
FROM fonoteca_cd
WHERE titulo_cd LIKE '%BSO%'
   OR titulo_cd LIKE '%soundtrack%'
   OR titulo_cd LIKE '%OST%'
   OR titulo_cd LIKE '%película%'
   OR titulo_cd LIKE '%cine%'
ORDER BY titulo_cd;
"""

# Ejecutar la consulta y cargar los datos en un DataFrame
df_cds = pd.read_sql_query(query_cds, conn)

# Consulta SQL para buscar canciones dentro de estos CDs con enlace a Spotify
query_canciones = """
SELECT interprete_cancion, cancion, cancion_url 
FROM fonoteca_canciones 
WHERE cancion_url IS NOT NULL
AND id IN (
    SELECT id FROM fonoteca_cd
    WHERE titulo_cd LIKE '%BSO%'
       OR titulo_cd LIKE '%soundtrack%'
       OR titulo_cd LIKE '%OST%'
       OR titulo_cd LIKE '%película%'
       OR titulo_cd LIKE '%cine%'
);
"""

# Ejecutar la consulta y cargar los datos en un DataFrame
df_canciones = pd.read_sql_query(query_canciones, conn)

# Cerrar la conexión a la base de datos
conn.close()

# Guardar los resultados en archivos Excel
df_cds.to_excel("CDs_relacionados_cine.xlsx", index=False)
df_canciones.to_excel("Canciones_relacionadas_cine.xlsx", index=False)

print("✔ Resultados guardados en 'CDs_relacionados_cine.xlsx' y 'Canciones_relacionadas_cine.xlsx'.")