import streamlit as st
import sqlite3
import pandas as pd
import os
import base64
import unicodedata
import sys


# 🔹 Asegurar que Python use UTF-8
sys.stdout.reconfigure(encoding='utf-8')
#
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
# st.sidebar.title("Consultar la Fonoteca")
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

# 📌 Ruta de la base de datos SQLite y de las imágenes
DB_PATH = "./db/FonotecaRadioUMH.db"
IMAGES_DIR = "./imagenes_cd/"

# 📌 Función para normalizar texto (elimina acentos y convierte a minúsculas)
def normalizar_texto(texto):
    if texto:
        texto = texto.lower()
        texto = ''.join(c for c in unicodedata.normalize('NFKC', texto))
    return texto

# 📌 Función para convertir una imagen local a base64
def convertir_imagen_a_base64(ruta_imagen):
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return None

# 📌 Función para realizar búsquedas en la base de datos
def buscar_canciones(criterio, tipo_busqueda):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 🔹 Normalizar el criterio de búsqueda
    criterio_normalizado = normalizar_texto(criterio)

    # 🔹 Consulta SQL con agrupación por `titulo_cd` y ordenación por `disc_number` y `track_number`
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
        WHERE {} LIKE ? COLLATE NOCASE
        GROUP BY fc.titulo_cd, fca.disc_number, fca.track_number
        ORDER BY fc.titulo_cd ASC, fca.disc_number ASC, fca.track_number ASC;
    """

    campo_busqueda = {
        "Canción": "fca.cancion",
        "Intérprete": "fca.interprete_cancion",
        "CD": "fc.titulo_cd"
    }.get(tipo_busqueda, None)

    if campo_busqueda is None:
        return pd.DataFrame()

    cursor.execute(query.format(campo_busqueda), ('%' + criterio_normalizado + '%',))
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        return pd.DataFrame()

    # 🔹 Convertir los resultados en un DataFrame
    df = pd.DataFrame(resultados, columns=["CARÁTULA", "NÚM", "TITULO", "AUTOR", "INTERPRETE", "CD", "PISTA", "CANCION", "URL"])
    return df

# 📌 Interfaz de Streamlit
st.markdown("<h2 style='color: #BD2830; text-align: center;'>Consultar la Fonoteca</h2>", unsafe_allow_html=True)

# 🔹 Selección de tipo de búsqueda
opcion = st.radio("Buscar por:", ["Canción", "Intérprete", "CD"])
criterio = st.text_input(f"Introduce el nombre de la {opcion.lower()}:")

# 🔹 Botón de búsqueda
if st.button("Buscar"):
    if criterio:
        resultados = buscar_canciones(criterio, opcion)

        if not resultados.empty:
            st.write(f"### Resultados encontrados ({len(resultados)}):")

            table_data = []

            for _, row in resultados.iterrows():
                caratula = row["CARÁTULA"]
                ruta_imagen = caratula.strip()  

                if ruta_imagen.startswith("http"):  # Si es una URL, mostrar directamente
                    caratula_display = f'<img src="{ruta_imagen}" width="80">'
                else:  # Si es una imagen local, verificar existencia
                    if os.path.exists(ruta_imagen):  
                        base64_str = convertir_imagen_a_base64(ruta_imagen)
                        caratula_display = f'<img src="data:image/jpeg;base64,{base64_str}" width="80">' if base64_str else "⚠️ Error al cargar la imagen"
                    else:
                        caratula_display = "❌ Imagen no encontrada"

                # 🔹 Si la URL está vacía o es NULL, solo mostramos el título sin enlace
                cancion_display = row["CANCION"]
                if row["URL"].strip():  
                    cancion_display = f'<a href="{row["URL"]}" target="_blank">{cancion_display}</a>'

                # 🔹 Agregar a la tabla
                table_data.append([
                    caratula_display, row["NÚM"], row["TITULO"], row["AUTOR"], 
                    row["INTERPRETE"], row["CD"], row["PISTA"], cancion_display
                ])

            # 🔹 Convertir la tabla en un DataFrame para mostrarla en HTML
            table_df = pd.DataFrame(table_data, columns=["CARÁTULA", "NÚM", "TITULO", "AUTOR", "INTERPRETE", "CD", "PISTA", "CANCION"])
            st.markdown(table_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.warning("No se encontraron resultados.")
    else:
        st.error("Por favor, introduce un criterio de búsqueda.")