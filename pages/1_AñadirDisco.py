import pandas as pd
import streamlit as st
import os
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
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
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Ruta del archivo Excel
input_excel_path = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

# Función para cargar datos
@st.cache_data
def cargar_datos():
    if os.path.exists(input_excel_path):
        return pd.read_excel(input_excel_path)
    return pd.DataFrame(columns=["Nº", "AUTOR", "NOMBRE CD", "TITULO", "URL", "ID"])

# Guardar datos en el archivo Excel
def guardar_datos(df):
    df.to_excel(input_excel_path, index=False)

# Función para buscar canciones en Spotify
def buscar_canciones(autor, nombre_cd):
    resultados = sp.search(q=f"album:{nombre_cd} artist:{autor}", type="album", limit=1)
    if resultados["albums"]["items"]:
        album_id = resultados["albums"]["items"][0]["id"]
        album_tracks = sp.album_tracks(album_id)
        canciones = [
            {
                "TITULO": track["name"],
                "URL": track["external_urls"]["spotify"],
                "ID": track["id"],
            }
            for track in album_tracks["items"]
        ]
        return canciones
    return []

# Título de la página
st.title("Fonoteca de Radio UMH - Añadir CD")

# Cargar datos existentes
datos = cargar_datos()

# Formulario para añadir un nuevo registro
with st.form("formulario_alta", clear_on_submit=True):
    nuevo_numero = st.text_input("Introduce el Nº (por ejemplo, 0001):")
    nuevo_autor = st.text_input("Introduce el AUTOR:")
    nuevo_nombre_cd = st.text_input("Introduce el NOMBRE CD:")

    # Botón para enviar el formulario
    submit = st.form_submit_button("Añadir registro y buscar canciones")

    if submit:
        if nuevo_numero and nuevo_autor and nuevo_nombre_cd:
            # Buscar canciones en Spotify
            canciones = buscar_canciones(nuevo_autor, nuevo_nombre_cd)

            if canciones:
                # Crear un DataFrame para las canciones encontradas
                canciones_df = pd.DataFrame(canciones)
                canciones_df["Nº"] = nuevo_numero
                canciones_df["AUTOR"] = nuevo_autor
                canciones_df["NOMBRE CD"] = nuevo_nombre_cd

                # Concatenar el nuevo registro
                datos = pd.concat([datos, canciones_df], ignore_index=True)

                # Guardar datos en Excel
                guardar_datos(datos)

                # Mostrar mensaje de éxito
                st.success(f"🎉 Se añadieron {len(canciones)} canciones del álbum '{nuevo_nombre_cd}' por '{nuevo_autor}'.")
            else:
                st.warning("⚠️ No se encontraron canciones para este álbum en Spotify.")
        else:
            st.error("Por favor, completa todos los campos antes de añadir el registro.")