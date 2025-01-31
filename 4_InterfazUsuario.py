import streamlit as st
import sqlite3
import pandas as pd
st.sidebar.title("Consultar la Fonoteca)
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
db_path = "FonotecaRadioUMH.db"  # La base de datos debe estar en el mismo directorio
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
    query_cds = f"SELECT DISTINCT nombre_cd, imagen_url FROM fonoteca WHERE {campo_busqueda} LIKE ? ORDER BY nombre_cd"
    cds_df = pd.read_sql_query(query_cds, conn, params=(f"%{busqueda}%",))

    # Convertir los resultados a lista
    cds_encontrados = cds_df["nombre_cd"].tolist()

    # Mostrar mensaje si no se encuentra ningún CD
    if not cds_encontrados:
        st.error(f"⚠️ No se encontraron resultados para '{busqueda}' en el campo '{campo_busqueda}'.")
        st.warning("🔍 Intenta con otro término de búsqueda o revisa la ortografía.")

# Mostrar el combo si hay CDs encontrados
if cds_encontrados:
    cd_seleccionado = st.selectbox("Selecciona un CD:", cds_encontrados)

    # Obtener la carátula del CD seleccionado
    imagen_url = cds_df.loc[cds_df["nombre_cd"] == cd_seleccionado, "imagen_url"].values[0]

    # Mostrar la carátula del CD si existe una URL válida
    if pd.notna(imagen_url) and imagen_url != "No disponible":
        st.image(imagen_url, caption=f"Carátula de {cd_seleccionado}", width=200)

    # Si el usuario selecciona un CD, mostrar las canciones de ese CD
    if cd_seleccionado:
        query_canciones = """
            SELECT numero, autor, nombre_cd, titulo, url
            FROM fonoteca
            WHERE nombre_cd = ?
            ORDER BY numero
        """
        canciones_df = pd.read_sql_query(query_canciones, conn, params=(cd_seleccionado,))

        # Convertir los títulos de las canciones en enlaces a Spotify
        def make_clickable(val, url):
            if pd.notna(url) and url != "No disponible":
                return f'<a href="{url}" target="_blank">{val}</a>'
            return val

        # Aplicar la conversión en la columna de títulos
        canciones_df["titulo"] = canciones_df.apply(lambda row: make_clickable(row["titulo"], row["url"]), axis=1)

        # Eliminar la columna de URL, ya que ahora está integrada en el título
        canciones_df.drop(columns=["url"], inplace=True)

        # Renombrar columnas a mayúsculas
        canciones_df.columns = [col.upper() for col in canciones_df.columns]

        # Aplicar estilos CSS para alinear cabeceras a la izquierda
        st.write(
            """
            <style>
                table th { text-align: left !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Mostrar la tabla con los resultados sin índice y con formato HTML
        st.write(f"Listado de canciones en el CD: **{cd_seleccionado}**")
        st.write(canciones_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Cerrar conexión con la base de datos
conn.close()