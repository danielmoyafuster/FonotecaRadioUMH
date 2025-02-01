import os
import streamlit as st
import sqlite3


#
# verificando la base de datos
#

db_path = "./db/FonotecaRadioUMH.db"

st.write("Archivos en el directorio actual:", os.listdir(os.getcwd()))
st.write("Archivos en la carpeta 'db':", os.listdir("./db"))
st.write("Base de datos existe:", os.path.exists(db_path))



st.write("Permisos del archivo:", os.stat(db_path))

#
# comprobando integridad de la base de datos
#

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    result = cursor.fetchone()
    st.write("Resultado de PRAGMA integrity_check:", result)
    conn.close()
except Exception as e:
    st.error(f"Error al abrir la base de datos: {e}")