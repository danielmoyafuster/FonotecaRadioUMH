import streamlit as st
import sqlite3

DB_PATH = "./db/FonotecaRadioUMH.db"

def get_genres():
    """
    Obtiene los géneros únicos de la base de datos desde la columna 'genero_musical'.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT genero_musical FROM fonoteca_cd WHERE genero_musical IS NOT NULL ORDER BY genero_musical")
    genres = [row[0] for row in cursor.fetchall()]
    conn.close()
    return genres

def get_cds_by_genre(genre):
    """
    Obtiene los CDs de un género específico.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT Id, titulo_cd FROM fonoteca_cd WHERE genero_musical = ? ORDER BY titulo_cd", (genre,))
    cds = cursor.fetchall()
    conn.close()
    return cds

def get_interpretes_by_cd(cd_id):
    """
    Obtiene los intérpretes de un CD específico.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT interprete_cancion FROM fonoteca_canciones WHERE Id = ? ORDER BY interprete_cancion", (cd_id,))
    interpretes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return interpretes

def get_songs_by_interprete(cd_id, interprete):
    """
    Obtiene las canciones de un intérprete dentro de un CD.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT cancion FROM fonoteca_canciones WHERE Id = ? AND interprete_cancion = ? ORDER BY cancion", (cd_id, interprete))
    songs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return songs

# 🔹 **Interfaz en Streamlit**
st.title("🎵 Navegación por la Fonoteca")

genres = get_genres()

if not genres:
    st.warning("⚠️ No hay géneros musicales registrados en la base de datos.")
else:
    # Selección de género
    selected_genre = st.selectbox("Selecciona un género musical:", genres)

    if selected_genre:
        cds = get_cds_by_genre(selected_genre)
        if not cds:
            st.info("📭 No hay CDs en este género.")
        else:
            # Selección de CD
            cd_options = {titulo: cd_id for cd_id, titulo in cds}
            selected_cd_title = st.selectbox("Selecciona un CD:", list(cd_options.keys()))
            selected_cd_id = cd_options[selected_cd_title]

            # Mostrar intérpretes
            interpretes = get_interpretes_by_cd(selected_cd_id)
            if not interpretes:
                st.info("🎤 No hay intérpretes en este CD.")
            else:
                selected_interpretes = st.multiselect("Selecciona intérpretes:", interpretes)

                # Mostrar canciones de los intérpretes seleccionados
                for interprete in selected_interpretes:
                    songs = get_songs_by_interprete(selected_cd_id, interprete)
                    if songs:
                        st.write(f"🎤 **{interprete}**")
                        for song in songs:
                            st.markdown(f"- 🎵 {song}")