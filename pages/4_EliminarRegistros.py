import pandas as pd
import streamlit as st
import sqlite3
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

# Ruta de la base de datos
db_path = "./db/FonotecaRadioUMH.db"

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Formulario para seleccionar el número de CD a eliminar
st.title("Eliminar un CD de la Fonoteca")
numero_cd = st.text_input("Introduce el Número del CD que quieres eliminar:")

if st.button("🔍 Buscar CD"):
    query = "SELECT numero, autor, nombre_cd, titulo, url FROM fonoteca WHERE numero = ?"
    df = pd.read_sql_query(query, conn, params=(numero_cd,))

    if df.empty:
        st.warning("⚠️ No se encontraron registros con ese número de CD.")
    else:
        # Convertir los títulos en enlaces activos
        df["titulo"] = df.apply(lambda row: f'<a href="{row["url"]}" target="_blank">{row["titulo"]}</a>', axis=1)

        # Eliminar la columna "url" de la tabla antes de mostrarla
        df.drop(columns=["url"], inplace=True)

        # Renombrar columnas a mayúsculas
        df.columns = [col.upper() for col in df.columns]

        # 📌 Aplicar estilos CSS para alinear cabeceras a la izquierda
        st.write(
            """
            <style>
                table th {
                    text-align: left !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Mostrar la tabla con los enlaces correctamente renderizados
        st.write("🎵 **Canciones encontradas:**")
        columnas_a_mostrar = ["NUMERO", "AUTOR", "NOMBRE_CD", "TITULO"]
        st.write(df[columnas_a_mostrar].to_html(escape=False, index=False), unsafe_allow_html=True)

if st.button("❌ Eliminar CD"):
    if numero_cd:
        cursor.execute("DELETE FROM fonoteca WHERE numero = ?", (numero_cd,))
        conn.commit()
        st.success(f"✅ Se han eliminado todos los registros con el Número de CD {numero_cd}.")
    else:
        st.warning("⚠️ Introduce un número de CD válido.")

# Cerrar la conexión
conn.close()