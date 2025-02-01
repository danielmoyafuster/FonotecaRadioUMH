import streamlit as st
import sqlite3
import pandas as pd

# Configurar la barra lateral
st.sidebar.title("Consultar la Fonoteca")
st.sidebar.markdown(
    '''
    <div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
        <a href="https://radio.umh.es/" target="_blank">
            <img src="https://radio.umh.es/files/2023/07/FOTO-PERFIL-RADIO.png" 
                 alt="Radio UMH" 
                 style="width: 150px; border-radius: 10px; margin-bottom: 10px;">
        </a>
        <p style="font-size: 16px; font-weight: bold; color: #333;">Gestión de la Fonoteca</p>
        <hr style="border: none; border-top: 1px solid #ccc; margin: 10px 0;">
    </div>
    ''',
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

    # Convertir los resultados a lista con "Autor - Nombre del CD"
    cds_encontrados = [f"{row['autor']} - {row['nombre_cd']}" for _, row in cds_df.iterrows()]

    # Contador de resultados
    num_cds_encontrados = len(cds_encontrados)

    # Mostrar mensaje si no se encuentra ningún CD
    if not cds_encontrados:
        st.error(f"⚠️ No se encontraron resultados para '{busqueda}' en el campo '{campo_busqueda}'.")
        st.warning("🔍 Intenta con otro término de búsqueda o revisa la ortografía.")

# Mostrar el combo si hay CDs encontrados
if cds_encontrados:
    cd_seleccionado = st.selectbox(f"Selecciona un CD ({num_cds_encontrados} encontrados):", cds_encontrados)

    if cd_seleccionado:
        # Extraer solo el nombre del CD sin el autor
        nombre_cd_real = cd_seleccionado.split(' - ', 1)[1] if ' - ' in cd_seleccionado else cd_seleccionado

        # Obtener la carátula del CD desde la base de datos
        query_imagen = 'SELECT imagen_url FROM fonoteca WHERE nombre_cd = ? LIMIT 1'
        imagen_df = pd.read_sql_query(query_imagen, conn, params=(nombre_cd_real,))

        if not imagen_df.empty and pd.notna(imagen_df['imagen_url'].iloc[0]) and imagen_df['imagen_url'].iloc[0] != 'No disponible':
            st.image(imagen_df['imagen_url'].iloc[0], caption=f"Carátula de {nombre_cd_real}", width=200)

        # Consultar las canciones del CD
        query_canciones = 'SELECT numero, titulo, url FROM fonoteca WHERE nombre_cd = ? ORDER BY numero'
        canciones_df = pd.read_sql_query(query_canciones, conn, params=(nombre_cd_real,))

        if not canciones_df.empty:
            st.write('Lista de Canciones:')

            # Convertir los títulos en enlaces clicables
            def make_clickable(val, url):
                if pd.notna(url) and url != "No disponible":
                    return f'<a href="{url}" target="_blank">{val}</a>'
                return val

            canciones_df["titulo"] = canciones_df.apply(lambda row: make_clickable(row["titulo"], row["url"]), axis=1)

            # Eliminar la columna URL, ya que está integrada en el título
            canciones_df.drop(columns=["url"], inplace=True)

            # Renombrar columnas a mayúsculas
            canciones_df.columns = [col.upper() for col in canciones_df.columns]

            # Mostrar la tabla con los resultados sin índice y con formato HTML
            st.write(canciones_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Cerrar conexión con la base de datos
conn.commit
conn.close()