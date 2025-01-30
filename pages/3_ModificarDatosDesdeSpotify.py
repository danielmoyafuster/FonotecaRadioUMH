import pandas as pd
import requests
import base64
import streamlit as st
import pyperclip  # Para copiar al portapapeles

#
# ACTUALIZACIÓN 30/01/25 06:00
#

# 📌 Función para copiar al portapapeles (sin notificaciones)
def copiar_al_portapapeles(texto):
    pyperclip.copy(texto)  # Copia el texto sin mostrar ninguna notificación

# 📌 Función para obtener token de Spotify
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

# 📌 Función para obtener información de un álbum usando su ID de Spotify
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
            "tracks": [{
                "title": track["name"], 
                "url": track["external_urls"]["spotify"] if "external_urls" in track and "spotify" in track["external_urls"] else None
            } for track in album_info["tracks"]["items"]]
        }
    return None

# 📌 Credenciales de Spotify
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

# 📌 Nombre del archivo Excel
EXCEL_FILE = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

# 📌 Cargar el archivo Excel y obtener álbumes no encontrados
@st.cache_data
def load_excel():
    try:
        df = pd.read_excel(EXCEL_FILE)
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo Excel.")
        return pd.DataFrame()

df = load_excel()

# 📌 Filtrar álbumes no encontrados
df_no_encontrados = df[df["TITULO"] == "Álbum no encontrado"]

# ✅ **Corrección del error** (asegurar que el DataFrame no está vacío)
if not df_no_encontrados.empty:  
    st.title("🎵 Corrección de Álbumes No Encontrados")
    
    # 🔹 Leyenda antes del ComboBox
    st.markdown("### 🎧 CD's no encontrados en SPOTIFY")

    # ComboBox para seleccionar un álbum
    opciones = df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1).tolist()
    
    col1, col2 = st.columns([4, 1])  # Dividir en columnas (ComboBox y botón)
    
    with col1:
        seleccion = st.selectbox("Selecciona un álbum para corregir:", opciones, key="album_selector")

    with col2:
        if st.button("📋 Copiar al portapapeles"):
            copiar_al_portapapeles(seleccion)

    # ✅ **Asegurar que el formulario aparece tras seleccionar un álbum**
    if seleccion:
        seleccion_index = df_no_encontrados[df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1) == seleccion].index[0]
        autor_original = df.loc[seleccion_index, "AUTOR"]
        nombre_cd_original = df.loc[seleccion_index, "NOMBRE CD"]
        num_original = df.loc[seleccion_index, "Nº"]

        # 🔹 Campo de texto para pegar el ID de Spotify (aparece correctamente ahora)
        album_id = st.text_input("🔗 Pega el ID del CD desde Spotify aquí:", key="spotify_id_input")

        # 🔍 Botón de búsqueda con ID de Spotify
        if album_id and st.button("🔍 Buscar en Spotify por ID"):
            token = get_spotify_token()
            if token:
                album_info = get_album_by_id(album_id, token)
                if album_info:
                    # ✅ Guardar la URL de la carátula correctamente en la Excel
                    image_url = album_info["image_url"] if album_info["image_url"] else "Sin imagen"

                    # ✅ Guardar todas las canciones con el mismo Nº, AUTOR y NOMBRE CD
                    track_rows = []
                    for track in album_info["tracks"]:
                        track_url = track["url"] if track["url"] else "URL no disponible"
                        track_rows.append({
                            "Nº": num_original,
                            "AUTOR": album_info["artist"],  
                            "NOMBRE CD": album_info["name"],  
                            "TITULO": track["title"],  
                            "URL": track_url,  # ✅ Guardando correctamente la URL de la canción
                            "ID": album_info["id"],
                            "IMAGEN_URL": image_url  
                        })

                    # Agregar las canciones al DataFrame con `pd.concat()`
                    if track_rows:
                        df = pd.concat([df, pd.DataFrame(track_rows)], ignore_index=True)

                    # ✅ Eliminar el registro original con "Álbum no encontrado"
                    df = df.drop(index=seleccion_index).reset_index(drop=True)

                    # ✅ Guardar la Excel con los cambios
                    df.to_excel(EXCEL_FILE, index=False)
                    st.success(f"✅ Álbum actualizado y guardado: {album_info['name']} ({album_info['artist']})")

                    # ✅ Mostrar la imagen del álbum si está disponible
                    if image_url != "Sin imagen":
                        st.image(image_url, caption="Carátula del Álbum", width=300)

                    # ✅ Mostrar el listado de canciones con URL a Spotify
                    st.markdown("### 🎶 Listado de Canciones")
                    for track in album_info["tracks"]:
                        track_url = track["url"] if track["url"] else "#"
                        st.markdown(f"- **[{track['title']}]({track_url})**")

                else:
                    st.error(f"❌ No se encontró el álbum con ID: {album_id}")

else:
    st.info("✅ No hay álbumes pendientes de corrección.")