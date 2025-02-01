import streamlit as st
import sqlite3
import pandas as pd

# Configurar la barra lateral
st.sidebar.title("Consultar la Fonoteca")
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
        <a href="https://radio.umh.es/" target="_blank">
            <img src="https://radio.umh.es/files/2023/07/FOTO-PERFIL-RADIO.png" 
                 alt="Radio UMH" 
                 style="width: 150px; border-radius: 10px; margin-bottom: 10px;">
        </a>
        <p style="font-size: 16px; font-weight: bold; color: #333;">Gestión de la Fonoteca</p>
        <hr style="border: none; border-top: 1px solid #ccc; margin: 10px 0;">
    </div>
    """,
    unsafe_allow_html=True,
)

# Configurar título de la app
st.title("Fonoteca Radio UMH")

# Conectar a la base de datos SQLite
db_path = "./db/FonotecaRadioUMH.db"
conn = sqlite3.connect(db_path)

# Campos permitidos para la búsqueda
campos_permitidos = ["numero", "autor", "nombre_cd", "titulo"]

# Seleccionar campo de búsqueda
campo_busqueda = st.selectbox("Selecciona un campo para buscar:", campos_permitidos)

# Entrada de búsqueda
busqueda = st.text_input("Introduce el término de búsqueda:")

# Inicializar variable para CDs encontrados
cds_encontrados = []

# Si hay una búsqueda activa
if busqueda:
    # Consultar los CDs donde se encuentran los criterios de búsqueda
    query_cds = f"SELECT DISTINCT autor, nombre_cd, imagen_url FROM fonoteca WHERE {campo_busqueda} LIKE ? ORDER BY nombre_cd"
    cds_df = pd.read_sql_query(query_cds, conn, params=(f"%{busqueda}%",))

    # Convertir los resultados a lista con el formato "Autor - Nombre del CD"
    cds_encontrados = [f"{row['autor']} - {row['nombre_cd']}" for _, row in cds_df.iterrows()]

    # Contador de resultados
    st.write(f"Resultados encontrados: {len(cds_encontrados)}")

# Combo para seleccionar un CD
cd_seleccionado = st.selectbox("Selecciona un CD:", cds_encontrados)

# Cerrar la conexión a la base de datos
conn.close()