import streamlit as st
import sqlite3
import pandas as pd
import os

# 📌 Configurar la barra lateral
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

# 📌 Configurar título de la app
st.title("Fonoteca Radio UMH")

# 📌 Conectar a la base de datos SQLite
db_path = os.path.join(os.getcwd(), "db", "FonotecaRadioUMH.db")
conn = sqlite3.connect(db_path)

# 📌 Desactivar modo WAL para evitar problemas en la conexión
conn.execute("PRAGMA journal_mode=DELETE;")
conn.commit()

# 📌 Campos permitidos para la búsqueda (ahora la búsqueda por "autor" se hace en `fonoteca_canciones`)
campos_permitidos = ["numero_cd", "autor", "titulo_cd", "cancion"]

# 📌 Seleccionar campo de búsqueda
campo_busqueda = st.selectbox("Selecciona un campo para buscar:", campos_permitidos)

# 📌 Entrada de búsqueda
busqueda = st.text_input("Introduce el término de búsqueda:")

# 📌 Inicializar variable para CDs encontrados
cds_encontrados = []

# 📌 Si hay una búsqueda activa
if busqueda:
    if campo_busqueda == "cancion":
        # 📌 Buscar en `fonoteca_canciones` por título de canción y obtener datos del CD desde `fonoteca_cd`
        query_cds = '''
            SELECT DISTINCT c.numero_cd, c.titulo_cd, c.autor, c.carátula_cd
            FROM fonoteca_cd c
            JOIN fonoteca_canciones s ON c.numero_cd = s.numero_cd
            WHERE s.cancion LIKE ?
            ORDER BY c.titulo_cd
        '''
    elif campo_busqueda == "autor":
        # 📌 Buscar en `fonoteca_canciones` por el intérprete de la canción y obtener datos del CD
        query_cds = '''
            SELECT DISTINCT c.numero_cd, c.titulo_cd, c.autor, c.carátula_cd
            FROM fonoteca_cd c
            JOIN fonoteca_canciones s ON c.numero_cd = s.numero_cd
            WHERE s.interprete_cancion LIKE ?
            ORDER BY c.titulo_cd
        '''
    else:
        # 📌 Buscar en `fonoteca_cd` para las otras opciones
        query_cds = f'''
            SELECT DISTINCT numero_cd, titulo_cd, autor, carátula_cd
            FROM fonoteca_cd
            WHERE {campo_busqueda} LIKE ?
            ORDER BY titulo_cd
        '''
    
    cds_df = pd.read_sql_query(query_cds, conn, params=(f"%{busqueda}%",))

    # 📌 Convertir los resultados a lista con "Número CD - Título CD - Autor"
    cds_encontrados = [f"{row['numero_cd']} - {row['titulo_cd']} - {row['autor']}" for _, row in cds_df.iterrows()]

    # 📌 Contador de resultados
    num_cds_encontrados = len(cds_encontrados)

    # 📌 Mostrar mensaje si no se encuentra ningún CD
    if not cds_encontrados:
        st.error(f"⚠️ No se encontraron resultados para '{busqueda}' en el campo '{campo_busqueda}'.")
        st.warning("🔍 Intenta con otro término de búsqueda o revisa la ortografía.")

# 📌 Mostrar el combo si hay CDs encontrados
if cds_encontrados:
    cd_seleccionado = st.selectbox(f"Selecciona un CD ({num_cds_encontrados} encontrados):", cds_encontrados)

    if cd_seleccionado:
        # 📌 Extraer número, título y autor del CD seleccionado
        partes = cd_seleccionado.split(' - ')
        numero_cd_real, titulo_cd_real, autor_cd_real = partes[0], partes[1], partes[2]

        # 📌 Obtener la carátula del CD desde la base de datos
        query_imagen = 'SELECT carátula_cd FROM fonoteca_cd WHERE numero_cd = ? LIMIT 1'
        imagen_df = pd.read_sql_query(query_imagen, conn, params=(numero_cd_real,))

        if not imagen_df.empty and pd.notna(imagen_df['carátula_cd'].iloc[0]) and imagen_df['carátula_cd'].iloc[0] != 'No disponible':
            st.image(imagen_df['carátula_cd'].iloc[0], caption=f"Carátula de {titulo_cd_real}", width=200)
        else:
            st.image("https://via.placeholder.com/200?text=Sin+Car%C3%A1tula", caption="Carátula no disponible", width=200)

        # 📌 Consultar las canciones del CD
        if campo_busqueda == "cancion":
            query_canciones = '''
                SELECT numero_cd, interprete_cancion, indice_cancion, cancion, cancion_url
                FROM fonoteca_canciones
                WHERE numero_cd = ? AND cancion LIKE ?
                ORDER BY indice_cancion
            '''
            canciones_df = pd.read_sql_query(query_canciones, conn, params=(numero_cd_real, f"%{busqueda}%"))
        elif campo_busqueda == "autor":
            query_canciones = '''
                SELECT numero_cd, interprete_cancion, indice_cancion, cancion, cancion_url
                FROM fonoteca_canciones
                WHERE numero_cd = ? AND interprete_cancion LIKE ?
                ORDER BY indice_cancion
            '''
            canciones_df = pd.read_sql_query(query_canciones, conn, params=(numero_cd_real, f"%{busqueda}%"))
        else:
            query_canciones = '''
                SELECT numero_cd, interprete_cancion, indice_cancion, cancion, cancion_url
                FROM fonoteca_canciones
                WHERE numero_cd = ?
                ORDER BY indice_cancion
            '''
            canciones_df = pd.read_sql_query(query_canciones, conn, params=(numero_cd_real,))

        if not canciones_df.empty:
            st.write('Lista de Canciones:')

            # 📌 Convertir los títulos en enlaces clicables
            def make_clickable(val, url):
                if pd.notna(url) and url != "No disponible":
                    return f'<a href="{url}" target="_blank">{val}</a>'
                return val

            canciones_df["cancion"] = canciones_df.apply(lambda row: make_clickable(row["cancion"], row["cancion_url"]), axis=1)

            # 📌 Eliminar la columna URL, ya que está integrada en el título
            canciones_df.drop(columns=["cancion_url"], inplace=True)

            # 📌 Renombrar columnas con los nombres correctos en MAYÚSCULAS
            canciones_df.columns = ["NÚMERO CD", "INTÉRPRETE", "ÍNDICE", "CANCIÓN"]

            # 📌 Mostrar la tabla
            st.write(canciones_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# 📌 Guardar cambios en la base de datos
conn.commit()
conn.close()