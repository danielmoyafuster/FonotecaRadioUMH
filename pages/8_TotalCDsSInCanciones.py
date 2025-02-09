
import streamlit as st
import sqlite3
import pandas as pd

# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# 8_TotalCDsSinCanciones.py
# Muestra el número total de Cds que no tienen canciones
# Versión 2.0 05/02/2025 10:07
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.


#
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
st.sidebar.title("Total de CDs sin canciones")
st.sidebar.caption("Versión 2.0 05/02/2025 10:07")
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
                <h1>CDs sin canciones</h1>
            </th>
        </tr>
    </table>
    ''',
    unsafe_allow_html=True,
)
#
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#

# 📌 Ruta de la base de datos
DB_PATH = "./db/FonotecaRadioUMH.db"

# 🔹 Definir la función para ejecutar la consulta
def ejecutar_consulta():
    consulta = """
    SELECT COUNT(*) AS total_cds_sin_canciones
    FROM fonoteca_cd
    WHERE id NOT IN (SELECT DISTINCT id FROM fonoteca_canciones);
    """

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(consulta)
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else 0
    except Exception as e:
        return f"❌ Error: {e}"

# 📌 Interfaz de Streamlit
st.markdown("<h2 style='color: #BD2830; text-align: center;'>CDs dados de alta sin canciones</h2>", unsafe_allow_html=True)

# 📌 Botón para ejecutar la consulta
if st.button("Mostrar CDs sin canciones"):
    with st.spinner("🔍 Consultando la base de datos..."):
        total_cds = ejecutar_consulta()
        st.success(f"📀 Hay **{total_cds} CDs** sin canciones registradas.")