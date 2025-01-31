import streamlit as st
import sqlite3
import pandas as pd

# Configurar título de la app
st.title("Editar Autor y Nombre del CD en la Fonoteca")

# Conectar a la base de datos SQLite
db_path = "./db/FonotecaRadioUMH.db"

# 🔍 Búsqueda por AUTOR o NOMBRE CD
st.subheader("Buscar CD para editar")
criterio_busqueda = st.radio("Buscar por:", ["Autor", "Nombre CD"])

busqueda = st.text_input("🔍 Introduce el texto de búsqueda:")

# Realizar la búsqueda si hay un criterio
if busqueda:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if criterio_busqueda == "Autor":
        query = "SELECT DISTINCT autor, nombre_cd FROM fonoteca WHERE autor LIKE ? ORDER BY autor, nombre_cd"
        cursor.execute(query, (f"%{busqueda}%",))
    else:
        query = "SELECT DISTINCT autor, nombre_cd FROM fonoteca WHERE nombre_cd LIKE ? ORDER BY autor, nombre_cd"
        cursor.execute(query, (f"%{busqueda}%",))

    resultados = cursor.fetchall()
    conn.close()

    if resultados:
        # Crear una lista desplegable con los resultados
        opciones = [f"{autor} - {nombre_cd}" for autor, nombre_cd in resultados]
        seleccion = st.selectbox("Selecciona el CD a editar:", opciones)

        # Obtener los valores actuales
        autor_actual, nombre_cd_actual = seleccion.split(" - ")

        # Mostrar los valores en campos editables
        st.subheader("Editar Datos del CD")
        nuevo_autor = st.text_input("✍️ Nuevo Autor:", value=autor_actual)
        nuevo_nombre_cd = st.text_input("🎵 Nuevo Nombre del CD:", value=nombre_cd_actual)

        # Botón para guardar cambios
        if st.button("💾 Guardar Cambios"):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Actualizar todos los registros con el mismo CD
            query_update = "UPDATE fonoteca SET autor = ?, nombre_cd = ? WHERE autor = ? AND nombre_cd = ?"
            cursor.execute(query_update, (nuevo_autor, nuevo_nombre_cd, autor_actual, nombre_cd_actual))
            conn.commit()
            conn.close()

            # Mensaje de éxito
            st.success(f"✅ CD actualizado correctamente: **{nuevo_autor} - {nuevo_nombre_cd}**")
            st.rerun()
    else:
        st.warning("⚠️ No se encontraron resultados con la búsqueda.")