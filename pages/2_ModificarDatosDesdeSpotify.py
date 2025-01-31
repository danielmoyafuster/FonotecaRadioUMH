import streamlit as st
import sqlite3
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Configuración de la barra lateral
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

# Configurar credenciales de Spotify
SPOTIFY_CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
SPOTIFY_CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                           client_secret=SPOTIFY_CLIENT_SECRET))

# Configurar título de la app
st.title("Actualizar Álbumes No Encontrados en Spotify")

# Función para cargar los álbumes no encontrados
def cargar_albumes_no_encontrados():
    conn = sqlite3.connect("FonotecaRadioUMH.db")
    query = """
        SELECT DISTINCT autor, nombre_cd FROM fonoteca
        WHERE titulo = 'Álbum no encontrado' 
        AND nombre_cd IS NOT NULL 
        AND TRIM(nombre_cd) != ''
        ORDER BY autor, nombre_cd
    """
    albumes_df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Eliminar valores "nan"
    albumes_df = albumes_df.dropna()
    
    return albumes_df

# Botón para recargar la lista manualmente
if st.button("🔄 Recargar Lista de Álbumes"):
    st.rerun()

# Cargar álbumes al inicio
albumes_df = cargar_albumes_no_encontrados()

# Contar el número de álbumes encontrados
num_albumes = len(albumes_df)

# Crear una lista de opciones en formato "AUTOR - NOMBRE CD"
if num_albumes > 0:
    albumes_df["combo_label"] = albumes_df["autor"] + " - " + albumes_df["nombre_cd"]
    album_dict = albumes_df.set_index("combo_label").to_dict("index")

    # Guardamos la selección en una variable de sesión para que se recargue después
    album_seleccionado_label = st.selectbox(f"Álbumes no encontrados en Spotify ({num_albumes}):", album_dict.keys())

    # Obtener datos del álbum seleccionado
    album_seleccionado = album_dict[album_seleccionado_label]["nombre_cd"]
    autor_seleccionado = album_dict[album_seleccionado_label]["autor"]

    # 🔹 Entrada de ID de Spotify (con key para evitar errores)
    spotify_album_id = st.text_input("🔗 Pega aquí la ID de Spotify del álbum seleccionado:", key="spotify_id_input")

    # Botón para buscar en Spotify y actualizar la base de datos
    if st.button("📥 Obtener datos del álbum y actualizar"):
        if spotify_album_id:
            # Obtener datos del álbum desde Spotify
            album_data = sp.album(f"spotify:album:{spotify_album_id}")

            # Obtener carátula
            album_cover = album_data["images"][0]["url"] if album_data["images"] else "No disponible"

            # Obtener lista de canciones
            track_list = []
            for track in album_data["tracks"]["items"]:
                track_list.append({
                    "numero": track["track_number"],
                    "autor": ", ".join([artist["name"] for artist in track["artists"]]),
                    "nombre_cd": album_data["name"],
                    "titulo": track["name"],
                    "url": track["external_urls"]["spotify"],
                    "spotify_id": track["id"],
                    "imagen_url": album_cover
                })

            # Convertir a DataFrame
            new_tracks_df = pd.DataFrame(track_list)

            # Conectar a SQLite para actualizar la base de datos
            conn = sqlite3.connect("FonotecaRadioUMH.db")
            cursor = conn.cursor()

            # Eliminar el registro antiguo con "Álbum no encontrado"
            cursor.execute("DELETE FROM fonoteca WHERE nombre_cd = ? AND autor = ?", (album_seleccionado, autor_seleccionado))
            conn.commit()

            # Insertar los nuevos datos en la base de datos
            new_tracks_df.to_sql("fonoteca", conn, if_exists="append", index=False)

            # Confirmar cambios y cerrar conexión
            conn.commit()
            conn.close()

            # 🔹 Mensaje de éxito y mostrar la carátula
            st.success(f"✅ El álbum '{album_seleccionado}' de {autor_seleccionado} ha sido actualizado con datos de Spotify.")
            st.image(album_cover, caption="Nueva carátula del álbum", width=300)

            # 🔹 Recargar la lista de álbumes después de actualizar (esto también limpia el input)
            st.rerun()

else:
    st.write("✅ No hay álbumes sin encontrar en Spotify.")