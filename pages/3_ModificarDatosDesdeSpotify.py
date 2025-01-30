import pandas as pd
import requests
import base64
import streamlit as st
import os



#
# ACTUALIZACIÓN 30/01/25 16:40
#
st.sidebar.title("Corregir Álbum (SPOTIFY)")
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

# ----------------------------------------------------------------------------------------------------



# 📌 Nombre del archivo Excel
EXCEL_FILE = "FONOTECA_CD_UMH_SPOTIFY.xlsx"



# 📌 Función para obtener el token de Spotify
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        st.error(f"⚠️ Error al obtener token: {response.text}")
    return None

# 📌 Función para obtener información del álbum por ID
def get_album_by_id(album_id, token):
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        album_info = response.json()
        return {
            "id": album_info["id"],
            "name": album_info["name"],
            "artist": album_info["artists"][0]["name"],
            "url": album_info["external_urls"]["spotify"],
            "image_url": album_info["images"][0]["url"] if album_info["images"] else None,
            "tracks": [
                {"title": track["name"], "url": track["external_urls"]["spotify"]}
                for track in album_info["tracks"]["items"]
            ]
        }
    else:
        st.error(f"⚠️ Error en la API de Spotify: {response.text}")
    return None  

# 📌 Función para cargar datos sin caché persistente
def load_excel():
    return pd.read_excel(EXCEL_FILE, engine="openpyxl")

st.title("🔍 Corrección de Álbumes No Encontrados - Spotify")

# 📌 Inicializar session_state para el ID del álbum si no existe
if "album_id" not in st.session_state:
    st.session_state["album_id"] = ""

# 📌 Botón para actualizar la lista y limpiar el campo de texto
if st.button("🔄 Actualizar Lista"):
    df = load_excel()  # Recargar datos
    df_no_encontrados = df[df["TITULO"] == "Álbum no encontrado"]
    st.session_state["album_id"] = ""  # 🔹 Limpiar el cuadro de texto
    st.experimental_rerun()

# 📌 Cargar el archivo en cada ejecución
df = load_excel()
df_no_encontrados = df[df["TITULO"] == "Álbum no encontrado"]

# 📌 Mostrar el selectbox con los álbumes no encontrados
if not df_no_encontrados.empty:
    opciones = df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1).tolist()
    seleccion = st.selectbox(f"Selecciona un álbum para buscar en Spotify ({len(opciones)} disponibles):", opciones, key="album_selector")

    # 📌 Obtener índice del álbum seleccionado
    seleccion_index = df_no_encontrados[
        df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1) == seleccion
    ].index[0]

    num_original = df.loc[seleccion_index, "Nº"]
    
    # 📌 Campo de entrada para el ID del álbum (usando session_state)
    album_id = st.text_input("🔗 Pega el ID del álbum desde Spotify:", value=st.session_state["album_id"], key="album_id_input")

    # 📌 Guardar el valor en session_state cada vez que cambia
    if album_id != st.session_state["album_id"]:
        st.session_state["album_id"] = album_id

    # 📌 Botón para buscar y corregir el álbum en Spotify
    if album_id and st.button("🔍 Buscar álbum en Spotify"):
        token = get_spotify_token()
        if token:
            album_info = get_album_by_id(album_id, token)

            if album_info:
                track_rows = [
                    {
                        "Nº": num_original,
                        "AUTOR": album_info["artist"],  
                        "NOMBRE CD": album_info["name"],  
                        "TITULO": track["title"],  
                        "URL": track["url"],  
                        "ID": album_info["id"],
                        "IMAGEN_URL": album_info["image_url"]  
                    }
                    for track in album_info["tracks"]
                ]

                if track_rows:
                    df = pd.concat([df, pd.DataFrame(track_rows)], ignore_index=True)
                    df.drop(index=seleccion_index, inplace=True)
                    df.reset_index(drop=True, inplace=True)

                    df.to_excel(EXCEL_FILE, index=False)

                    st.success(f"✅ Álbum '{album_info['name']}' corregido y guardado con sus canciones.")

                    if album_info["image_url"]:
                        st.image(album_info["image_url"], caption=f"📀 {album_info['name']} - {album_info['artist']}", use_container_width=True)

                    st.markdown("### 🎼 Canciones del CD:")
                    for idx, track in enumerate(album_info["tracks"], start=1):
                        st.markdown(f"🎵 {idx}. **[{track['title']}]({track['url']})**")

                    # 🔄 Limpiar el campo de ID después de guardar
                    st.session_state["album_id"] = ""