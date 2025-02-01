import streamlit as st
import sqlite3
import pandas as pd
import os

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

# Conectar a la base de datos SQLite con una ruta segura
db_path = os.path.join(os.getcwd(), "db", "FonotecaRadioUMH.db")
conn = sqlite3.connect(db_path)

# Desactivar modo WAL para evitar problemas en la conexión
conn.execute("PRAGMA journal_mode=DELETE;")
conn.commit()

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
    query_cds = '''
        SELECT DISTINCT numero, nombre_cd, autor, imagen_url
        FROM fonoteca
        WHERE CAST({} AS TEXT) LIKE ?
        ORDER BY nombre_cd
    '''.format(campo_busqueda)

    cds_df = pd.read_sql_query(query_cds, conn, params=(f"%{busqueda}%",))

    # Convertir los resultados a lista con "Número CD - Nombre CD - Autor"
    cds_encontrados = [f"{row['numero']} - {row['nombre_cd']} - {row['autor']}" for _, row in cds_df.iterrows()]

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
        # Extraer número, nombre y autor del CD seleccionado
        partes = cd_seleccionado.split(' - ')
        numero_cd_real, nombre_cd_real, autor_cd_real = partes[0], partes[1], partes[2]

        # Obtener la carátula del CD desde la base de datos
        query_imagen = 'SELECT imagen_url FROM fonoteca WHERE nombre_cd = ? LIMIT 1'
        imagen_df = pd.read_sql_query(query_imagen, conn, params=(nombre_cd_real,))

        if not imagen_df.empty and pd.notna(imagen_df['imagen_url'].iloc[0]) and imagen_df['imagen_url'].iloc[0] != 'No disponible':
            st.image(imagen_df['imagen_url'].iloc[0], caption=f"Carátula de {nombre_cd_real}", width=200)
        else:
            st.image("https://via.placeholder.com/200?text=Sin+Car%C3%A1tula", caption="Carátula no disponible", width=200)

        # Consultar las canciones del CD
        if campo_busqueda == "autor":
            query_canciones = '''
                SELECT numero, nombre_cd, autor, titulo, url
                FROM fonoteca
                WHERE nombre_cd = ? AND autor = ?
                ORDER BY titulo
            '''
            canciones_df = pd.read_sql_query(query_canciones, conn, params=(nombre_cd_real, busqueda))
        else:
            query_canciones = '''
                SELECT numero, nombre_cd, autor, titulo, url
                FROM fonoteca
                WHERE nombre_cd = ?
                ORDER BY titulo
            '''
            canciones_df = pd.read_sql_query(query_canciones, conn, params=(nombre_cd_real,))

        if not canciones_df.empty:
            st.write('Lista de Canciones:')

            # Generar índice de canción (1, 2, 3, ...)
            canciones_df.insert(3, "ÍNDICE", range(1, len(canciones_df) + 1))

            # Convertir los títulos en enlaces clicables
            def make_clickable(val, url):
                if pd.notna(url) and url != "No disponible":
                    return f'<a href="{url}" target="_blank">{val}</a>'
                return val

            canciones_df["titulo"] = canciones_df.apply(lambda row: make_clickable(row["titulo"], row["url"]), axis=1)

            # Eliminar la columna URL, ya que está integrada en el título
            canciones_df.drop(columns=["url"], inplace=True)

            # Renombrar columnas con los nombres correctos en MAYÚSCULAS
            canciones_df.columns = ["NÚMERO", "NOMBRE CD", "AUTOR", "ÍNDICE", "TÍTULO"]

            # Estilos CSS para alinear la cabecera a la izquierda
            st.write(
                """
                <style>
                    table th { text-align: left !important; }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # Mostrar la tabla con los resultados correctamente ordenados
            st.write(canciones_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Guardar cambios en la base de datos
conn.commit()
conn.close()