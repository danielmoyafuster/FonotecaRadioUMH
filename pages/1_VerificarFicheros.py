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

import os
import sqlite3
import streamlit as st

# Asegurar que la carpeta 'db' existe
db_folder = os.path.abspath("db")
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# Usar una ruta absoluta para la base de datos
db_path = os.path.join(db_folder, "FonotecaRadioUMH.db")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    st.write("Tablas en la base de datos:", tablas)
    conn.close()
except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")