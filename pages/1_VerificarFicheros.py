import os
import streamlit as st


#
# verificando la base de datos
#

db_path = "./db/FonotecaRadioUMH.db"

st.write("Archivos en el directorio actual:", os.listdir(os.getcwd()))
st.write("Archivos en la carpeta 'db':", os.listdir("./db"))
st.write("Base de datos existe:", os.path.exists(db_path))



st.write("Permisos del archivo:", os.stat(db_path))