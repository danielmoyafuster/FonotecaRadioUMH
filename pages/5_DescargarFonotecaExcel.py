import pandas as pd
import streamlit as st
import sqlite3
import datetime
import io  # Para manejar la descarga en memoria
st.sidebar.title("Descargar Base de Datos (EXCEL)")
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

# Ruta de la base de datos
db_path = "./db/FonotecaRadioUMH.db"

# Configurar título de la app
st.title("📤 Exportar Base de Datos a Excel")

# Botón de descarga
if st.button("📥 Descargar Base de Datos en Excel"):
    # Conectar a la base de datos y obtener la tabla completa
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM fonoteca"
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Verificar si la base de datos tiene registros
    if df.empty:
        st.warning("⚠️ No hay datos en la base de datos para exportar.")
    else:
        # Generar nombre del archivo con la fecha actual
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d")
        nombre_archivo = f"FonotecaRadioUMH_{fecha_actual}.xlsx"

        # Crear un buffer en memoria para guardar el archivo
        output = io.BytesIO()

        # Guardar DataFrame en un archivo Excel en memoria
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Fonoteca", index=False)
        output.seek(0)  # Volver al inicio del buffer

        # Preparar la descarga
        st.download_button(
            label="⬇️ Descargar Archivo",
            data=output,
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("✅ Exportación completada. Descarga el archivo con el botón de arriba.")