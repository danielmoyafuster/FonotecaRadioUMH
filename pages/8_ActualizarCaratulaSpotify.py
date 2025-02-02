import streamlit as st
import sqlite3
import requests

# 📌 Configuración de la base de datos SQLite
DB_PATH = "./db/FonotecaRadioUMH.db"

# 📌 Credenciales de Spotify
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"
AUTH_URL = "https://accounts.spotify.com/api/token"

def obtener_token_spotify():
    """ Obtiene el token de autenticación de Spotify """
    response = requests.post(AUTH_URL, {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })
    data = response.json()
    return data.get("access_token")

def obtener_caratula_spotify(id_cd_spotify, token):
    """ Obtiene la URL de la carátula de un CD en Spotify """
    url = f"https://api.spotify.com/v1/albums/{id_cd_spotify}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    # 📀 Extraer la URL de la carátula si existe
    return data["images"][0]["url"] if "images" in data and data["images"] else None

def obtener_cds_sin_caratula():
    """ Obtiene los CDs que tienen id_cd pero no tienen carátula """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo_cd, id_cd FROM fonoteca_cd WHERE id_cd IS NOT NULL AND carátula_cd IS NULL;")
    cds = cursor.fetchall()
    conn.close()
    return cds

def actualizar_caratula_cd(id_cd_local, caratula_url):
    """ Actualiza el campo carátula_cd en la tabla fonoteca_cd """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE fonoteca_cd SET carátula_cd = ? WHERE id = ?;", (caratula_url, id_cd_local))
    conn.commit()
    conn.close()

# 📌 Interfaz de Streamlit
st.sidebar.title("Actualizar Carátulas desde Spotify")

# 🔹 Obtener la lista de CDs sin carátula pero con `id_cd`
cds_sin_caratula = obtener_cds_sin_caratula()

if not cds_sin_caratula:
    st.success("✅ Todos los CDs con `id_cd` ya tienen carátula.")
else:
    opciones = {f"{titulo} (ID Spotify: {id_cd})": (id, id_cd) for id, titulo, id_cd in cds_sin_caratula}
    seleccion = st.selectbox("Selecciona un CD sin carátula:", list(opciones.keys()))

    if st.button("Actualizar Carátula"):
        id_cd_local, id_cd_spotify = opciones[seleccion]

        # 📌 Obtener token de Spotify
        token = obtener_token_spotify()

        # 📌 Obtener la carátula del CD desde Spotify
        caratula_url = obtener_caratula_spotify(id_cd_spotify, token)

        if caratula_url:
            # 📌 Actualizar la base de datos con la carátula
            actualizar_caratula_cd(id_cd_local, caratula_url)
            st.image(caratula_url, caption="Carátula actualizada", width=200)
            st.success("📀 Carátula descargada y guardada correctamente.")
        else:
            st.warning("⚠️ No se encontró carátula para este CD en Spotify.")