# import os
# #mport streamlit as st
# import sqlite3


#
# verificando la base de datos
#

# db_path = "./db/FonotecaRadioUMH.db"

# st.write("Archivos en el directorio actual:", os.listdir(os.getcwd()))
# st.write("Archivos en la carpeta 'db':", os.listdir("./db"))
# st.write("Base de datos existe:", os.path.exists(db_path))


#
# revisar los permisos de la base de datos
#
# st.write("Permisos del archivo:", os.stat(db_path))

#
# comprobando integridad de la base de datos
#
# try:
#    conn = sqlite3.connect(db_path)
#    cursor = conn.cursor()
#    cursor.execute("PRAGMA integrity_check;")
#    result = cursor.fetchone()
#    st.write("Resultado de PRAGMA integrity_check:", result)
#    conn.close()
#except Exception as e:
#    st.error(f"Error al abrir la base de datos: {e}")

import sqlite3
import streamlit as st

db_path = "./db/FonotecaRadioUMH.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Contar cuántos registros hay en la tabla fonoteca
    cursor.execute("SELECT COUNT(*) FROM fonoteca;")
    total_registros = cursor.fetchone()[0]

    # Mostrar algunos registros de ejemplo
    cursor.execute("SELECT * FROM fonoteca LIMIT 5;")
    muestras = cursor.fetchall()

    st.write(f"Total de registros en fonoteca: {total_registros}")
    st.write("Ejemplo de registros en fonoteca:", muestras)

    conn.close()
except Exception as e:
    st.error(f"Error al consultar la base de datos: {e}")

#
# reparar base de datos
#


db_path = "./db/FonotecaRadioUMH.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    result = cursor.fetchone()
    st.write("Resultado de PRAGMA integrity_check:", result)
    conn.close()
except Exception as e:
    st.error(f"Error al verificar la base de datos: {e}")
