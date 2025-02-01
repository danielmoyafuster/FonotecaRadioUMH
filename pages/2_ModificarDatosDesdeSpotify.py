import streamlit as st
import sqlite3
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# 📌 Configurar la barra lateral
st.sidebar.title("Modificar Datos (SPOTIFY)")
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

# 📌 Configurar credenciales de Spotify
SPOTIFY_CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
SPOTIFY_CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                           client_secret=SPOTIFY_CLIENT_SECRET))

# 📌 Configurar título de la app
st.title("Actualizar Álbumes No Encontrados en Spotify")

# 📌 Ruta de la base de datos con una conexión segura
db_path = os.path.join(os.getcwd(), "db", "FonotecaRadioUMH.db")

# 📌 Asegurar que la base de datos se pueda abrir
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA journal_mode=DELETE;")
conn.commit()
conn.close()

# 📌 Función para cargar los álbumes no encontrados
def cargar_albumes_no_encontrados():
    with sqlite3.connect(db_path) as conn:
        query = """
            SELECT DISTINCT numero, autor, nombre_cd 
            FROM fonoteca
            WHERE titulo = 'Álbum no encontrado' 
            AND nombre_cd IS NOT NULL 
            AND TRIM(nombre_cd) != ''
            ORDER BY autor, nombre_cd
        """
        albumes_df = pd.read_sql_query(query, conn)

    # Eliminar valores "nan"
    albumes_df = albumes_df.dropna()
    
    return albumes_df

# 🔄 Botón para recargar la lista de álbumes
if st.button("🔄 Recargar Lista de Álbumes"):
    st.session_state["spotify_id_input"] = ""  # Vaciar el campo de ID
    st.rerun()

# 📌 Cargar álbumes al inicio
albumes_df = cargar_albumes_no_encontrados()

# Contar el número de álbumes encontrados
num_albumes = len(albumes_df)

# 📌 Crear una lista de opciones en formato "NÚMERO - AUTOR - NOMBRE CD"
if num_albumes > 0:
    albumes_df["combo_label"] = albumes_df["numero"].astype(str) + " - " + albumes_df["autor"] + " - " + albumes_df["nombre_cd"]
    album_dict = albumes_df.set_index("combo_label").to_dict("index")

    # Selección del álbum en la lista desplegable
    album_seleccionado_label = st.selectbox(f"Álbumes no encontrados en Spotify ({num_albumes}):", album_dict.keys())

    # Obtener datos del álbum seleccionado
    album_info = album_dict[album_seleccionado_label]
    numero_cd_seleccionado = album_info["numero"]
    nombre_cd_seleccionado = album_info["nombre_cd"]
    autor_seleccionado = album_info["autor"]

    # 📌 Entrada de ID de Spotify
    spotify_album_id = st.text_input(
        "🔗 Pega aquí la ID de Spotify del álbum seleccionado:",
        value=st.session_state.get("spotify_id_input", "")
    )

    # 📌 Botón para buscar en Spotify y actualizar la base de datos
    if st.button("📥 Obtener datos del álbum y actualizar"):
        if spotify_album_id:
            # Guardar la ID en session_state para mantenerla actualizada
            st.session_state["spotify_id_input"] = spotify_album_id

            # Obtener datos del álbum desde Spotify
            album_data = sp.album(f"spotify:album:{spotify_album_id}")

            # Obtener carátula
            album_cover = album_data["images"][0]["url"] if album_data["images"] else "No disponible"

            # Obtener lista de canciones y generar índice dinámico
            track_list = []
            for idx, track in enumerate(album_data["tracks"]["items"], start=1):
                track_list.append({
                    "numero": numero_cd_seleccionado,
                    "nombre_cd": album_data["name"],
                    "autor": ", ".join([artist["name"] for artist in track["artists"]]),
                    "indice": idx,
                    "titulo": track["name"],
                    "url": track["external_urls"]["spotify"],
                    "spotify_id": track["id"],
                    "imagen_url": album_cover
                })

            # Convertir a DataFrame asegurando tipos de datos correctos
            new_tracks_df = pd.DataFrame(track_list)

            # 📌 Conectar a SQLite para actualizar la base de datos
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # 📌 Eliminar el registro antiguo con "Álbum no encontrado"
                cursor.execute("DELETE FROM fonoteca WHERE nombre_cd = ? AND autor = ?", (nombre_cd_seleccionado, autor_seleccionado))
                conn.commit()

                # 📌 Insertar los nuevos datos en la base de datos
                for _, row in new_tracks_df.iterrows():
                    cursor.execute("""
                        INSERT INTO fonoteca (numero, nombre_cd, autor, titulo, url, spotify_id, imagen_url) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (row["numero"], row["nombre_cd"], row["autor"], row["titulo"], row["url"], row["spotify_id"], row["imagen_url"]))

                conn.commit()

            # 📌 Mensaje de éxito y mostrar la carátula
            st.success(f"✅ El álbum '{nombre_cd_seleccionado}' de {autor_seleccionado} ha sido actualizado con datos de Spotify.")
            st.image(album_cover, caption="Nueva carátula del álbum", width=300)

            # 📌 Vaciar la ID y recargar lista
            st.session_state["spotify_id_input"] = ""
            st.rerun()

else:
    st.write("✅ No hay álbumes sin encontrar en Spotify.")