import streamlit as st
import sqlite3
import requests
import time

# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# 5_AñadirCancionesManual.py
# Añadir canciones manualmente a CDs que no se encontraron en SPOTIFY
# Versión 2.0 05/02/2025 10:07
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.



#
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
st.sidebar.title("Buscar en SPOTIFY las Canciones Añadidas manualmente")
st.sidebar.caption("Versión 2.0 06/02/2025 16:18")
st.markdown(
    '''
    <style>
        /* 🔹 Quitar bordes de la tabla */
        table {
            border-collapse: collapse;
            border: none;
            background: transparent;
            width: 100%;
        }

        /* 🔹 Quitar bordes y fondo de las celdas */
        th, td {
            border: none !important;
            background: transparent !important;
            padding: 10px;
        }

        /* 🔹 Ajustar tamaño y estilos de la imagen */
        .logo-container img {
            width: 180px;  /* Aumentamos un poco el tamaño */
            border-radius: 10px;
            transition: transform 0.2s;
        }

        /* 🔹 Efecto hover en la imagen */
        .logo-container img:hover {
            transform: scale(1.1); /* Hace que la imagen se agrande un poco al pasar el ratón */
        }

        /* 🔹 Centrar el título */
        .title-container h1 {
            color: #BD2830;
            text-align: center;
            font-size: 30px;
        }
    </style>

    <table>
        <tr>
            <th class="logo-container">
                <a href="https://radio.umh.es/" target="_blank">
                    <img src="https://radio.umh.es/files/2023/07/FOTO-PERFIL-RADIO.png" 
                         alt="Radio UMH">
                </a>
            </th>
            <th class="title-container">
                <h1>Consultar la Fonoteca</h1>
            </th>
        </tr>
    </table>
    ''',
    unsafe_allow_html=True,
)
#
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#

# 📌 Configuración de la base de datos SQLite
DB_PATH = "./db/FonotecaRadioUMH.db"

# 📌 Credenciales de Spotify
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

# 📌 URLs de la API de Spotify
AUTH_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"

# 📌 Obtener token de acceso de Spotify
def get_spotify_token():
    response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    data = response.json()
    return data.get("access_token")

# 📌 Buscar canción en Spotify
def search_song_on_spotify(artist, track, token):
    headers = {"Authorization": f"Bearer {token}"}
    query = f"track:{track} artist:{artist}"
    params = {"q": query, "type": "track", "limit": 1}
    response = requests.get(SEARCH_URL, headers=headers, params=params)
    data = response.json()

    # Verificar si hay resultados
    if data.get("tracks") and data["tracks"]["items"]:
        song = data["tracks"]["items"][0]
        return song["external_urls"]["spotify"]
    
    return ""  # Si no se encuentra, se deja vacío

# 📌 Obtener canciones sin URL en la base de datos
def obtener_canciones_sin_url():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Id, interprete_cancion, cancion
        FROM fonoteca_canciones
        WHERE no_buscar = 0
        AND (cancion_url IS NULL OR cancion_url = '');
    """)
    canciones = cursor.fetchall()
    conn.close()
    return canciones

# 📌 Actualizar URL de la canción en la base de datos usando id, interprete_cancion y cancion
def actualizar_cancion_url(id_cancion, interprete, titulo, url):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE fonoteca_canciones 
        SET cancion_url = ? 
        WHERE id = ? AND interprete_cancion = ? AND cancion = ?;
    """, (url, id_cancion, interprete, titulo))
    conn.commit()
    conn.close()

# 📌 Interfaz de Streamlit
st.markdown("<h2 style='color: #BD2830; text-align: center;'>Buscar en SPOTIFY las Canciones Añadidas manualmente</h2>", unsafe_allow_html=True)
st.write("Este módulo busca en Spotify las canciones que no tienen una URL y las actualiza en la base de datos.")

# 🔹 Botón para iniciar la actualización
if st.button("Buscar y Actualizar Canciones en Spotify"):
    canciones = obtener_canciones_sin_url()

    if not canciones:
        st.success("✅ Todas las canciones tienen URL. No hay nada que actualizar.")
    else:
        token = get_spotify_token()
        total_canciones = len(canciones)
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, (id_cancion, interprete, titulo) in enumerate(canciones):
            url = search_song_on_spotify(interprete, titulo, token)
            actualizar_cancion_url(id_cancion, interprete, titulo, url)
            
            # 🔹 Actualizar barra de progreso y estado
            progress_bar.progress((i + 1) / total_canciones)
            status_text.text(f"Procesando: {titulo} - {interprete} ({i+1}/{total_canciones})")
            
            time.sleep(1)  # Simulación de retardo

        st.success("✅ Proceso completado. Todas las canciones han sido actualizadas.")