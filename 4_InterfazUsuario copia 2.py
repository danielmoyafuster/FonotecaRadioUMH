import streamlit as st
import sqlite3
import pandas as pd
import os
import base64
import unicodedata
import sys
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# Interfaz de Usuario - Pantalla Principal
# Versión 4.0 12/02/2025 14:23
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

# 🔹 Asegurar que Python use UTF-8
sys.stdout.reconfigure(encoding='utf-8')
#
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
st.sidebar.title("Consultar la Fonoteca")
st.sidebar.caption("Versión 4.0 12/02/2025 14:23")
st.markdown(
    '''
    <style>
        /* 🔹 Quitar bordes de la tabla */
        table {
            border-collapse: collapse;
            border: none;
            background: transparent;
            width: 100%;
        }

        /* 🔹 Quitar bordes y fondo de las celdas */
        th, td {
            border: none !important;
            background: transparent !important;
            padding: 10px;
        }

        /* 🔹 Ajustar tamaño y estilos de la imagen */
        .logo-container img {
            width: 180px;  /* Aumentamos un poco el tamaño */
            border-radius: 10px;
            transition: transform 0.2s;
        }

        /* 🔹 Efecto hover en la imagen */
        .logo-container img:hover {
            transform: scale(1.1); /* Hace que la imagen se agrande un poco al pasar el ratón */
        }

        /* 🔹 Centrar el título */
        .title-container h1 {
            color: #BD2830;
            text-align: center;
            font-size: 30px;
        }
    </style>

    <table>
        <tr>
            <th class="logo-container">
                <a href="https://radio.umh.es/" target="_blank">
                    <img src="https://radio.umh.es/files/2023/07/FOTO-PERFIL-RADIO.png" 
                         alt="Radio UMH">
                </a>
            </th>
            <th class="title-container">
                <h1>Consultar la Fonoteca</h1>
            </th>
        </tr>
    </table>
    ''',
    unsafe_allow_html=True,
)
#
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#
import streamlit as st
import sqlite3
import pandas as pd
import os
import base64
import unicodedata
import sys

# 🔹 Asegurar que Python use UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 📌 Ruta de la base de datos SQLite
DB_PATH = "./db/FonotecaRadioUMH.db"

# 📌 Función para normalizar texto
def normalizar_texto(texto):
    if texto:
        texto = texto.lower()
        texto = ''.join(c for c in unicodedata.normalize('NFKC', texto))
    return texto

# 📌 Función para convertir imagen local a base64
def convertir_imagen_a_base64(ruta_imagen):
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return None

# 📌 Función para buscar en la base de datos
def buscar_canciones(criterio):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 🔹 Normalizar criterio de búsqueda
    criterio_normalizado = f"%{normalizar_texto(criterio)}%"

    # 🔹 Consulta SQL en múltiples campos
    query = """
        SELECT 
            COALESCE(fc.carátula_cd, '') AS CARÁTULA,
            fc.numero_cd AS NÚM,   
            fc.titulo_cd AS TITULO,
            fc.autor AS AUTOR,
            COALESCE(fca.interprete_cancion, 'N/A') AS INTERPRETE,
            COALESCE(fca.disc_number, 0) AS CD,  
            COALESCE(fca.track_number, 0) AS PISTA,
            COALESCE(fca.cancion, 'SIN CANCIONES REGISTRADAS') AS CANCION,
            COALESCE(fca.cancion_url, '') AS URL
        FROM fonoteca_cd fc
        LEFT JOIN fonoteca_canciones fca ON fc.id = fca.id
        WHERE 
            LOWER(fc.numero_cd) LIKE ? OR
            LOWER(fc.titulo_cd) LIKE ? OR
            LOWER(fc.autor) LIKE ? OR
            LOWER(fca.interprete_cancion) LIKE ? OR
            LOWER(fca.cancion) LIKE ?
        GROUP BY fc.titulo_cd, fca.disc_number, fca.track_number
        ORDER BY fc.titulo_cd ASC, fca.disc_number ASC, fca.track_number ASC;
    """

    cursor.execute(query, (criterio_normalizado, criterio_normalizado, criterio_normalizado, criterio_normalizado, criterio_normalizado))
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        return pd.DataFrame()

    # 🔹 Convertir resultados en un DataFrame
    df = pd.DataFrame(resultados, columns=["CARÁTULA", "NÚM", "TITULO", "AUTOR", "INTERPRETE", "CD", "PISTA", "CANCION", "URL"])
    return df

# 📌 Interfaz de Streamlit
st.markdown("<h2 style='color: #BD2830; text-align: center;'>Consultar la Fonoteca</h2>", unsafe_allow_html=True)

# 🔹 Campo de búsqueda libre
criterio = st.text_input("Introduce un término de búsqueda (Titulo-CD, Canción, Intérprete, Número de CD):")

# 🔹 Botón de búsqueda
if st.button("Buscar"):
    if criterio:
        resultados = buscar_canciones(criterio)

        if not resultados.empty:
            st.write(f"### Resultados encontrados ({len(resultados)}):")

            table_data = []

            for idx, row in resultados.iterrows():
                caratula = row["CARÁTULA"]
                ruta_imagen = caratula.strip()

                # 🔹 Si la imagen es una URL o una imagen local
                if ruta_imagen.startswith("http"):
                    imagen_display = f'<img src="{ruta_imagen}" width="80">'
                else:
                    if os.path.exists(ruta_imagen):
                        base64_str = convertir_imagen_a_base64(ruta_imagen)
                        if base64_str:
                            img_tag = f"data:image/jpeg;base64,{base64_str}"
                            imagen_display = f'<img src="{img_tag}" width="80">'
                        else:
                            imagen_display = "⚠️ No se pudo cargar la imagen."
                    else:
                        imagen_display = "❌ Imagen no encontrada."

                # 🔹 Si la URL está vacía, solo mostrar el título
                cancion_display = row["CANCION"]
                if row["URL"].strip():
                    cancion_display = f'<a href="{row["URL"]}" target="_blank">{cancion_display}</a>'

                # 🔹 Agregar fila a la tabla
                table_data.append([
                    imagen_display, row["NÚM"], row["TITULO"], row["AUTOR"], 
                    row["INTERPRETE"], row["CD"], row["PISTA"], cancion_display
                ])

            # 🔹 Convertir la tabla a HTML
            table_html = "<table><tr><th>Carátula</th><th>Número</th><th>Título</th><th>Autor</th><th>Intérprete</th><th>CD</th><th>Pista</th><th>Canción</th></tr>"
            for row in table_data:
                table_html += "<tr>" + "".join(f"<td>{col}</td>" for col in row) + "</tr>"
            table_html += "</table>"

            # 🔹 Mostrar la tabla
            st.markdown(table_html, unsafe_allow_html=True)

        else:
            st.warning("No se encontraron resultados.")
    else:
        st.error("Por favor, introduce un criterio de búsqueda.")