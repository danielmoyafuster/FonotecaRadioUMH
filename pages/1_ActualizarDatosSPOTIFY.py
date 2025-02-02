import streamlit as st
import sqlite3
st.title ("Actualizar Datos desde SPOTIFY")

# Ruta de la base de datos SQLite
DB_PATH = "./db/FonotecaRadioUMH.db"

def obtener_cds_sin_id_cd():
    """ Obtiene los CDs que no tienen un id_cd en Spotify """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo_cd, autor FROM fonoteca_cd WHERE id_cd IS NULL OR id_cd = '';")
    cds = cursor.fetchall()
    conn.close()
    return cds

def actualizar_id_cd(cd_id, nuevo_id_cd):
    """ Actualiza el id_cd de un CD en la base de datos """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE fonoteca_cd SET id_cd = ? WHERE id = ?;", (nuevo_id_cd, cd_id))
    conn.commit()
    conn.close()

# 🔹 Título de la aplicación
st.markdown("<h2 style='color: #BD2830; text-align: center;'>Asignar manualmente ID de Spotify</h2>", unsafe_allow_html=True)

# 🔹 Obtener la lista de CDs sin id_cd
cds_sin_id = obtener_cds_sin_id_cd()

if not cds_sin_id:
    st.success("✅ Todos los CDs tienen un `id_cd`. No hay nada que actualizar.")
else:
    # 🔹 Mostrar un selectbox con los CDs sin id_cd
    opciones = {f"{titulo} - {autor}": id_cd for id_cd, titulo, autor in cds_sin_id}
    seleccion = st.selectbox("Selecciona un CD sin `id_cd`:", list(opciones.keys()))

    # 🔹 Cuadro de texto para ingresar el nuevo ID de Spotify
    nuevo_id_cd = st.text_input("Introduce el `id_cd` de Spotify:")

    # 🔹 Botón para actualizar la base de datos
    if st.button("Actualizar CD en la base de datos"):
        if nuevo_id_cd.strip():
            cd_id = opciones[seleccion]
            actualizar_id_cd(cd_id, nuevo_id_cd)
            st.success(f"✅ `id_cd` actualizado correctamente para **{seleccion}**.")
            st.warning("📢 Ahora debes ejecutar **8_ActualizarDesdeSpotify.py** para sincronizar las canciones.")
        else:
            st.error("⚠️ Debes ingresar un `id_cd` antes de actualizar.")