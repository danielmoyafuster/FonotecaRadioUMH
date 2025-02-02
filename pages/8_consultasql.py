
import streamlit as st
import sqlite3
import pandas as pd

# 📌 Ruta de la base de datos
DB_PATH = "./db/FonotecaRadioUMH.db"

# 🔹 Definir la función ANTES de llamarla
def ejecutar_consulta(sql_query):
    'sql_query = "SELECT * FROM fonoteca_cd WHERE titulo_cd LIKE '%RESERVADA%';"
    sql_query="SELECT COUNT(*) FROM fonoteca_cd WHERE id_cd IS NULL OR id_cd = '';"
    
    """ Ejecuta una consulta SQL y devuelve los resultados en un DataFrame """
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
st.sidebar.title("Ejecutar Comandos SQL")
st.markdown("<h2 style='color: #BD2830; text-align: center;'>Consulta SQL Directa</h2>", unsafe_allow_html=True)

if isinstance(resultado, pd.DataFrame) and not resultado.empty:
    st.write("### Resultados de la consulta:")
    st.dataframe(resultado)
else:
    st.warning("⚠️ No se encontraron resultados para 'RESERVADA'.")