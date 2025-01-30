import pandas as pd
import requests
import base64
import streamlit as st
import os
import pyperclip  # 📋 Para copiar al portapapeles
#
# ACTUALIZACIÓN 30/01/25 06:00
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


# 📌 Función para copiar texto al portapapeles (sin notificar al usuario)
def copiar_al_portapapeles(texto):
    pyperclip.copy(texto)


# 📌 Nombre del archivo Excel
EXCEL_FILE = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

# 📌 Función para obtener el token de autenticación de Spotify
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

# 📌 Función para obtener información del álbum desde Spotify
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
    return None  # Si no se encuentra el álbum

# 📌 Cargar el archivo Excel
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

if not df_no_encontrados.empty:  
    st.title("Corrección de Álbumes No Encontrados - Spotify")

    # 📌 Crear opciones para el `selectbox` con el número de elementos
    opciones = df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1).tolist()
    num_elementos = len(opciones)  # 📌 Contar el número de álbumes en la lista

    # 📌 Mostrar el selectbox con la cantidad de álbumes disponibles
    seleccion = st.selectbox(f"🎧 Selecciona un álbum para buscar en Spotify ({num_elementos} disponibles):", opciones, key="album_selector")

    # 📌 Botón para copiar el álbum seleccionado al portapapeles
    if st.button("📋 Copiar al portapapeles"):
        copiar_al_portapapeles(seleccion)

    if seleccion:
        # 🔹 Obtener el índice exacto de la fila seleccionada
        seleccion_index = df_no_encontrados[
            df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1) == seleccion
        ].index[0]

        autor_original = df.loc[seleccion_index, "AUTOR"]
        nombre_cd_original = df.loc[seleccion_index, "NOMBRE CD"]
        num_original = df.loc[seleccion_index, "Nº"]

        # 1️⃣ Campo para pegar el ID del álbum de Spotify
        album_id = st.text_input("🔗 Pega el ID del álbum desde Spotify:")

        # 2️⃣ Botón para buscar el álbum en Spotify
        if album_id and st.button("🔍 Buscar álbum en Spotify"):
            token = get_spotify_token()  # Obtener el token de autenticación
            if not token:
                st.error("❌ No se pudo obtener el token de autenticación de Spotify.")
            else:
                album_info = get_album_by_id(album_id, token)

                if album_info:
                    # ✅ Obtener las canciones del álbum
                    track_rows = []
                    for track in album_info["tracks"]:
                        track_rows.append({
                            "Nº": num_original,
                            "AUTOR": album_info["artist"],  
                            "NOMBRE CD": album_info["name"],  
                            "TITULO": track["title"],  
                            "URL": track["url"],  
                            "ID": album_info["id"],
                            "IMAGEN_URL": album_info["image_url"]  
                        })

                    # ✅ Agregar las canciones al DataFrame y eliminar solo la fila específica con "Álbum no encontrado"
                    if track_rows:
                        df = pd.concat([df, pd.DataFrame(track_rows)], ignore_index=True)
                        df = df.drop(index=seleccion_index).reset_index(drop=True)

                        # ✅ Guardar cambios en la Excel
                        df.to_excel(EXCEL_FILE, index=False)

                        # ✅ Mostrar mensaje de éxito SIN limpiar la pantalla
                        st.success(f"✅ Álbum '{album_info['name']}' corregido y guardado con sus canciones.")

                        # 📌 Mostrar la carátula del álbum después de guardar los datos
                        if album_info["image_url"]:
                            st.image(album_info["image_url"], caption=f"📀 {album_info['name']} - {album_info['artist']}", use_container_width=True)

                        # 📌 Listar todas las canciones con enlaces activos después de guardar los datos
                        st.markdown("### 🎼 Canciones del CD:")
                        for idx, track in enumerate(album_info["tracks"], start=1):
                            st.markdown(f"🎵 {idx}. **[{track['title']}]({track['url']})**")

                        # 🔄 **Actualizar la lista del ComboBox de forma segura**
                        df_no_encontrados = df[df["TITULO"] == "Álbum no encontrado"]
                        opciones = df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1).tolist()
                        
                        # **Eliminar la clave antes de modificar `session_state` para evitar errores**
                        st.session_state.pop("album_selector", None)  

                        if opciones:
                            # ✅ Actualizar el selectbox con los álbumes restantes
                            st.session_state.album_selector = opciones[0]  
                        else:
                            # ✅ Vaciar el selectbox si no hay más álbumes por corregir
                            st.session_state.album_selector = None  

                    else:
                        st.warning("⚠️ No se encontraron canciones para este álbum.")
                else:
                    st.error("❌ No se pudo recuperar la información del álbum de Spotify.")