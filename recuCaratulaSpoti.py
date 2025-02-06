import sqlite3
import requests
import time
import streamlit as st
from tqdm import tqdm  # 🔹 Barra de progreso para la terminal

# 📌 Configuración de la base de datos y Spotify
DB_PATH = "./db/FonotecaRadioUMH.db"
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"
AUTH_URL = "https://accounts.spotify.com/api/token"

# 📌 Obtener token de autenticación en Spotify
def obtener_token_spotify():
    response = requests.post(AUTH_URL, {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })
    data = response.json()
    return data.get("access_token")

# 📌 Obtener la carátula del álbum desde Spotify
def obtener_caratula_spotify(id_cd_spotify, token):
    url = f"https://api.spotify.com/v1/albums/{id_cd_spotify}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers).json()

    # 🔹 Si hay imágenes, devolver la URL de la carátula
    if "images" in response and response["images"]:
        return response["images"][0]["url"]  # 🔹 Primera imagen del álbum
    return None  # 🔹 No se encontró imagen

# 📌 Buscar y actualizar carátulas en la base de datos con barra de progreso
def actualizar_caratulas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 🔹 Obtener CDs con ID de Spotify pero sin carátula
    cursor.execute("""
        SELECT id, id_cd FROM fonoteca_cd 
        WHERE (carátula_cd IS NULL OR carátula_cd = '') 
        AND id_cd IS NOT NULL AND id_cd != ''
    """)
    cds_sin_caratula = cursor.fetchall()

    if not cds_sin_caratula:
        st.success("✅ No hay CDs pendientes de actualizar.")
        conn.close()
        return

    total_cds = len(cds_sin_caratula)
    st.write(f"🔍 CDs sin carátula encontrados: **{total_cds}**")

    token = obtener_token_spotify()

    # 🔹 Barra de progreso en Streamlit
    progress_bar = st.progress(0)

    with tqdm(total=total_cds, desc="🔄 Buscando carátulas en Spotify", unit=" CD") as pbar:
        for index, (id_cd_local, id_cd_spotify) in enumerate(cds_sin_caratula):
            st.write(f"🎵 Buscando carátula para CD **ID {id_cd_local}** en Spotify...")

            caratula_url = obtener_caratula_spotify(id_cd_spotify, token)

            if caratula_url:
                cursor.execute("UPDATE fonoteca_cd SET carátula_cd = ? WHERE id = ?", (caratula_url, id_cd_local))
                st.success(f"✅ Carátula guardada para CD ID {id_cd_local}.")
            else:
                st.warning(f"⚠️ No se encontró carátula para CD ID {id_cd_local}.")

            # 🔹 Actualizar barra de progreso
            progress_bar.progress((index + 1) / total_cds)
            pbar.update(1)

            time.sleep(0.5)  # 🔹 Pausa corta para evitar bloqueos de la API

    conn.commit()
    conn.close()
    st.success("🎵 ¡Todas las carátulas han sido actualizadas correctamente!")

# 📌 Ejecutar la actualización de carátulas en Streamlit
st.title("📀 Actualizar Carátulas de CDs desde Spotify")
st.write("Este módulo buscará en Spotify las carátulas de los CDs que no tienen imagen registrada.")

if st.button("🔄 Iniciar búsqueda y actualización"):
    actualizar_caratulas()