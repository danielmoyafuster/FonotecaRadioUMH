import streamlit as st
import sqlite3
import pandas as pd
import os
# st.title ("Consultar la Fonoteca 06:06")
import streamlit as st


# 📌 Configurar la barra lateral
st.sidebar.title("Consultar la Fonoteca")

st.markdown(
     '''
     <table border=0>
        <tr>
            <th>
                <div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
                    <a href="https://radio.umh.es/" target="_blank">
                        <img src="https://radio.umh.es/files/2023/07/FOTO-PERFIL-RADIO.png" 
                        alt="Radio UMH" 
                        style="width: 150px; border-radius: 10px; margin-bottom: 10px;">
                    </a>
                </div>
            </th>
            <th>
                <h1 style="color: #BD2830; text-align: center;">Consultar la Fonoteca</h1>
            </th>
        </tr>
    </table>

    ''',
    unsafe_allow_html=True,
)
# Ruta de la base de datos SQLite
DB_PATH = "./db/FonotecaRadioUMH.db"
#
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.--.
#


# 🔹 Función para realizar búsquedas en la base de datos
def buscar_canciones(criterio, tipo_busqueda):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ✅ Relación corregida con `id`
    query = """
        SELECT 
            fc.carátula_cd AS CARÁTULA,
            fc.numero_cd AS NÚM,   
            fc.autor AS AUTOR,
            fc.titulo_cd AS TITULO,
            fca.interprete_cancion AS INTERPRETE,
            fca.disc_number AS CD,  
            fca.track_number AS PISTA,
            fca.cancion AS CANCION,
            fca.cancion_url AS URL
        FROM fonoteca_canciones fca
        JOIN fonoteca_cd fc ON fc.id = fca.id  -- ✅ Relación corregida
        WHERE LOWER({}) LIKE LOWER(?);
    """

    campo_busqueda = {
        "Canción": "fca.cancion",
        "Intérprete": "fca.interprete_cancion",
        "CD": "fc.titulo_cd"
    }.get(tipo_busqueda, None)

    if campo_busqueda is None:
        st.error("Error interno: Tipo de búsqueda no válido.")
        return pd.DataFrame()

    cursor.execute(query.format(campo_busqueda), ('%' + criterio.lower() + '%',))
    resultados = cursor.fetchall()

    conn.close()

    if not resultados:
        return pd.DataFrame()

    # 🔹 Convertir los resultados en un DataFrame con nombres correctos
    df = pd.DataFrame(resultados, columns=["CARÁTULA", "NÚM", "AUTOR", "TITULO", "INTERPRETE", "CD", "PISTA", "CANCION", "URL"])

    # 🔹 Convertir la columna "CANCION" en un enlace activo si hay URL
    df["CANCION"] = df.apply(lambda row: f'<a href="{row["URL"]}" target="_blank">{row["CANCION"]}</a>' if row["URL"] else row["CANCION"], axis=1)

    return df.drop(columns=["URL"])  # Eliminamos la columna URL para no mostrarla directamente

# 🔹 Agregar estilos CSS para mejorar la visualización
st.markdown("""
    <style>
        /* Ajustar la tabla para que ocupe más espacio */
        .main .block-container {
            max-width: 100%;
            padding-top: 20px;
        }

        /* Estilizar la tabla con alineación a la izquierda */
        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            text-align: left;
            padding: 10px;
            font-size: 16px;
        }
        td {
            padding: 10px;
            font-size: 14px;
        }

        /* Ajustar la columna "CARÁTULA" para que las imágenes sean visibles */
        th:nth-child(1), td:nth-child(1) {
            width: 120px;
            text-align: center;
        }

        /* Ajustar la columna "CANCION" para que sea más ancha */
        th:nth-child(8), td:nth-child(8) {
            min-width: 250px;
        }
    </style>
""", unsafe_allow_html=True)

# 🔹 Selección de tipo de búsqueda
opcion = st.radio("Buscar por:", ["Canción", "Intérprete", "CD"])
criterio = st.text_input(f"Introduce el nombre de la {opcion.lower()}:")

# 🔹 Botón de búsqueda
if st.button("Buscar"):
    if criterio:
        resultados = buscar_canciones(criterio, opcion)

        if not resultados.empty:
            st.write(f"### Resultados encontrados ({len(resultados)}):")

            # 🔹 Convertir la columna "CARÁTULA" en una imagen clickeable
            resultados["CARÁTULA"] = resultados["CARÁTULA"].apply(
                lambda url: f'<a href="{url}" target="_blank"><img src="{url}" width="80" style="cursor: zoom-in;"></a>' if pd.notna(url) else "No disponible"
            )

            # 🔹 Mostrar la tabla con imágenes y enlaces clickeables
            st.markdown(resultados.to_html(escape=False, index=False), unsafe_allow_html=True)

        else:
            st.warning("No se encontraron resultados.")
    else:
        st.error("Por favor, introduce un criterio de búsqueda.")