import pandas as pd
import streamlit as st
import sqlite3
import os

# 📌 Configurar la barra lateral
st.sidebar.title("Eliminar Registros")
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
        <a href="https://radio.umh.es/" target="_blank">
            <img src="https://radio.umh.es/files/2023/07/FOTO-PERFIL-RADIO.png" 
                 alt="Radio UMH" 
                 style="width: 150px; border-radius: 10px; margin-bottom: 10px;">
        </a>
        <p style="font-size: 16px; font-weight: bold; color: #333;">Gestión de la Fonoteca</p>
        <hr style="border: none; border-top: 1px solid #ccc; margin: 10px 0;">
    </div>
    """,
    unsafe_allow_html=True,
)

# 📌 Ruta de la base de datos con una conexión segura
db_path = os.path.join(os.getcwd(), "db", "FonotecaRadioUMH.db")

# 📌 Asegurar que la base de datos se pueda abrir
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA journal_mode=DELETE;")
conn.commit()
conn.close()

# 📌 Título principal
st.title("Eliminar un CD de la Fonoteca")

# 📌 Entrada del número de CD a eliminar
numero_cd = st.text_input("Introduce el Número del CD que quieres eliminar:").strip()

# 📌 Inicializar `st.session_state` para almacenar la tabla de resultados temporalmente
if "consulta_resultados" not in st.session_state:
    st.session_state.consulta_resultados = None

# 📌 Botón para buscar el CD en la base de datos
if st.button("🔍 Buscar CD"):
    with sqlite3.connect(db_path) as conn:
        query = "SELECT numero, autor, nombre_cd, titulo, url FROM fonoteca WHERE numero = ?"
        df = pd.read_sql_query(query, conn, params=(numero_cd,))

    if df.empty:
        st.warning("⚠️ No se encontraron registros con ese número de CD.")
        st.session_state.consulta_resultados = None
    else:
        # 📌 Convertir los títulos en enlaces clicables sin alterar la estructura de la base de datos
        df["titulo"] = df.apply(lambda row: f'<a href="{row["url"]}" target="_blank">{row["titulo"]}</a>', axis=1)

        # 📌 Eliminar la columna "url" ya que está integrada en el título
        df.drop(columns=["url"], inplace=True)

        # 📌 Renombrar columnas en MAYÚSCULAS
        df.columns = ["NÚMERO", "AUTOR", "NOMBRE CD", "TÍTULO"]

        # 📌 Guardar resultados en `st.session_state`
        st.session_state.consulta_resultados = df

        # 📌 Aplicar estilos CSS para alinear cabeceras a la izquierda
        st.write(
            """
            <style>
                table th { text-align: left !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # 📌 Mostrar la tabla con los resultados
        st.write("🎵 **Canciones encontradas en el CD:**")
        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

# 📌 Botón para eliminar el CD (solo si hay resultados en `st.session_state`)
if st.session_state.consulta_resultados is not None:
    if st.button("❌ Eliminar CD"):
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fonoteca WHERE numero = ?", (numero_cd,))
            conn.commit()

        st.success(f"✅ Se han eliminado todos los registros con el Número de CD {numero_cd}.")
        
        # 📌 Vaciar `st.session_state` después de eliminar
        st.session_state.consulta_resultados = None
        st.rerun()