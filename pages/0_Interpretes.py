import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import streamlit as st

# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# 0_Interpretes.py
# Listado NUBE de PALABRAS donde se muestran los interpretes
# Versión 2.0 05/02/2025 10:07
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

# 📌 Configurar la barra lateral
st.sidebar.title("Consultar la Fonoteca")
st.sidebar.caption("Versión 2.0 05/02/2025 10:07")
#
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
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
# 📌 Interfaz de Streamlit
st.markdown("<h2 style='color: #BD2830; text-align: center;'>Nube de Interpretes</h2>", unsafe_allow_html=True)
#
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#

# Conectar con la base de datos
db_path = "./db/FonotecaRadioUMH.db"

def generar_nube_de_palabras():
    try:
        conn = sqlite3.connect(db_path)

        # Consultar los intérpretes y contar cuántas veces aparecen
        query = """
        SELECT interprete_cancion, COUNT(*) as total
        FROM fonoteca_canciones
        WHERE interprete_cancion IS NOT NULL AND interprete_cancion != ''
        GROUP BY interprete_cancion
        ORDER BY total DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            st.warning("No hay datos de intérpretes en la fonoteca.")
            return

        # Crear un diccionario con los intérpretes y su frecuencia
        word_freq = dict(zip(df["interprete_cancion"], df["total"]))

        # Generar la nube de palabras
        wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="viridis").generate_from_frequencies(word_freq)

        # Mostrar la nube de palabras en Streamlit
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        ax.set_title("Intérpretes en la Fonoteca", fontsize=16)
        
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error al generar la nube de palabras: {e}")


# Generar la nube de palabras automáticamente al cargar la página
generar_nube_de_palabras()