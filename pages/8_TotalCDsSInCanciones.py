
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


# 🔹 Definir la función ANTES de llamarla
def ejecutar_consulta(sql_query):
    # sql_query = "SELECT * FROM fonoteca_cd WHERE titulo_cd LIKE '%RESERVADA%';"
    sql_query = "SELECT COUNT(*) FROM fonoteca_cd WHERE id_cd IS NULL OR id_cd = '';"

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)

        # Si la consulta devuelve resultados, los obtenemos
        if sql_query.strip().lower().startswith("select"):
            datos = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(datos, columns=columnas)
            conn.close()
            return df
        else:
            conn.commit()
            conn.close()
            return "✅ Consulta ejecutada correctamente."

    except Exception as e:
        return f"❌ Error: {e}"

# 📌 Ahora definimos la consulta
consulta = "SELECT * FROM fonoteca_cd WHERE titulo_cd LIKE '%RESERVADA%';"
resultado = ejecutar_consulta(consulta)

# 📌 Interfaz de Streamlit
st.markdown("<h2 style='color: #BD2830; text-align: center;'>CDs dados de alta sin canciones</h2>", unsafe_allow_html=True)

if isinstance(resultado, pd.DataFrame) and not resultado.empty:
    st.write("### Resultados de la consulta:")
    st.dataframe(resultado)
else:
    st.warning("⚠️ No se encontraron resultados para 'RESERVADA'.")