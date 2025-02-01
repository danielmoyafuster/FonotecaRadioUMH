import streamlit as st
import sqlite3
import pandas as pd
import os

# 📌 Configurar título de la app
st.title("Editar Autor y Nombre del CD en la Fonoteca")

# 📌 Ruta de la base de datos con una conexión segura
db_path = os.path.join(os.getcwd(), "db", "FonotecaRadioUMH.db")

# 📌 Asegurar que la base de datos se pueda abrir
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA journal_mode=DELETE;")
conn.commit()
conn.close()

# 📌 Inicializar `st.session_state` para almacenar los resultados temporalmente
if "resultados_busqueda" not in st.session_state:
    st.session_state.resultados_busqueda = None

# 📌 Búsqueda por AUTOR o NOMBRE CD
st.subheader("🔍 Buscar CD para editar")
criterio_busqueda = st.radio("Buscar por:", ["Autor", "Nombre CD"])

busqueda = st.text_input("Introduce el texto de búsqueda:").strip()

# 📌 Realizar la búsqueda si hay un criterio válido
if busqueda:
    with sqlite3.connect(db_path) as conn:
        if criterio_busqueda == "Autor":
            query = "SELECT DISTINCT autor, nombre_cd FROM fonoteca WHERE autor LIKE ? ORDER BY autor, nombre_cd"
        else:
            query = "SELECT DISTINCT autor, nombre_cd FROM fonoteca WHERE nombre_cd LIKE ? ORDER BY autor, nombre_cd"

        resultados = pd.read_sql_query(query, conn, params=(f"%{busqueda}%",))

    if not resultados.empty:
        # 📌 Crear una lista desplegable con los resultados
        opciones = [f"{row['autor']} - {row['nombre_cd']}" for _, row in resultados.iterrows()]
        seleccion = st.selectbox("Selecciona el CD a editar:", opciones)

        # 📌 Obtener los valores actuales
        autor_actual, nombre_cd_actual = seleccion.split(" - ")

        # 📌 Mostrar los valores en campos editables
        st.subheader("✍️ Editar Datos del CD")
        nuevo_autor = st.text_input("Nuevo Autor:", value=autor_actual)
        nuevo_nombre_cd = st.text_input("Nuevo Nombre del CD:", value=nombre_cd_actual)

        # 📌 Botón para guardar cambios con confirmación
        if st.button("💾 Guardar Cambios"):
            if nuevo_autor and nuevo_nombre_cd:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()

                    # 📌 Actualizar todos los registros con el mismo CD
                    query_update = """
                        UPDATE fonoteca 
                        SET autor = ?, nombre_cd = ? 
                        WHERE autor = ? AND nombre_cd = ?
                    """
                    cursor.execute(query_update, (nuevo_autor, nuevo_nombre_cd, autor_actual, nombre_cd_actual))
                    conn.commit()

                # 📌 Mensaje de éxito y recarga de la búsqueda
                st.success(f"✅ CD actualizado correctamente: **{nuevo_autor} - {nuevo_nombre_cd}**")
                st.session_state.resultados_busqueda = None
                st.rerun()
            else:
                st.warning("⚠️ Los campos no pueden estar vacíos.")
    else:
        st.warning("⚠️ No se encontraron resultados con la búsqueda.")