
import streamlit as st
import sqlite3
import requests
import json
import os

# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# 1_AñadirCD.py
# Añadir un nuevo Cd a la fonoteca
# Versión 3.0 13/02/2025 11:18
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.



#
# configurar la estetica de la página
#
st.set_page_config(layout="wide")
#
# 📌 Configurar la barra lateral
st.sidebar.title("Añadir CD")
st.sidebar.caption("Versión 3.0 13/02/2025 11:18")
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
                <h1>Añadir CD</h1>
            </th>
        </tr>
    </table>
    ''',
    unsafe_allow_html=True,
)
# 📌 Configuración de credenciales de Spotify y DiscoGs
SPOTIFY_CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
SPOTIFY_CLIENT_SECRET  = "62f90ff98a2d4602968a488129aeae31"
DISCOGS_TOKEN = "EukYFBrBTzuhIlBCRcNmFUjFqGWtKHjGFQoqRdiv"
# 📌 Base de datos SQLite
DB_PATH = "./db/FonotecaRadioUMH.db"
#
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#


# 📌 Obtener el token de Spotify
def obtener_token_spotify():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

# 📌 Buscar CD en Spotify
def buscar_en_spotify(titulo_cd, autor, token):
    url = "https://api.spotify.com/v1/search"
    params = {"q": f"album:{titulo_cd} artist:{autor}", "type": "album", "limit": 1}
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data["albums"]["items"]:
            album = data["albums"]["items"][0]
            imagenes = album.get("images", [])
            caratula_url = imagenes[0]["url"] if imagenes else None  

            return {
                "id_cd": album["id"],
                "carátula_cd": caratula_url,
                "genero_musical": album.get("genres", ["Desconocido"])[0] if album.get("genres") else "Desconocido"
            }
    return None  # No encontrado

# 📌 Buscar canciones en Spotify
def buscar_canciones_spotify(id_cd, token):
    url = f"https://api.spotify.com/v1/albums/{id_cd}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        canciones = []
        for i, track in enumerate(data["items"], start=1):
            canciones.append({
                "disc_number": track["disc_number"],
                "track_number": track["track_number"],
                "cancion": track["name"],
                "interprete_cancion": ", ".join(artist["name"] for artist in track["artists"]),
                "cancion_url": track["external_urls"]["spotify"]
            })
        return canciones
    return []  # No se encontraron canciones

# 📌 Buscar CD en Discogs
# 📌 Buscar CD en Discogs y obtener la carátula correcta
# 📌 Buscar CD en Discogs y asegurarse de obtener el release correcto
def buscar_en_discogs(titulo_cd, autor):
    url = "https://api.discogs.com/database/search"
    params = {
        "artist": autor,
        "release_title": titulo_cd,
        "type": "release",
        "token": DISCOGS_TOKEN
    }
    headers = {"User-Agent": "MyDiscogsApp"}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            best_match = None
            mejor_puntaje = 0  # Para evaluar la mejor coincidencia
            
            for release in data["results"]:
                titulo_encontrado = release["title"].lower()
                titulo_buscado = f"{autor.lower()} - {titulo_cd.lower()}"
                
                # 🔹 Asignamos un puntaje en base a coincidencia exacta en el título
                puntaje = 0
                if titulo_encontrado == titulo_buscado:
                    puntaje += 3  # Coincidencia exacta = puntaje alto
                elif titulo_cd.lower() in titulo_encontrado:
                    puntaje += 2  # Coincidencia parcial
                elif autor.lower() in titulo_encontrado:
                    puntaje += 1  # Coincidencia solo por autor
                
                if puntaje > mejor_puntaje:
                    mejor_puntaje = puntaje
                    best_match = release
            
            # Si encontramos un release con mejor coincidencia, lo usamos
            if best_match:
                id_cd = best_match["id"]
                caratula_url = best_match.get("cover_image", None)
                
                print(f"🎯 Release ID seleccionado: {id_cd} ({best_match['title']})")
                
                return {
                    "id_cd": id_cd,
                    "carátula_cd": caratula_url,
                    "genero_musical": best_match.get("genre", ["Desconocido"])[0] if "genre" in best_match else "Desconocido"
                }

    return None  # No encontrado

# 📌 Buscar canciones en Discogs
def buscar_canciones_discogs(id_cd):
    url = f"https://api.discogs.com/releases/{id_cd}"
    headers = {"User-Agent": "MyDiscogsApp"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        canciones = []
        if "tracklist" in data:
            for track in data["tracklist"]:
                canciones.append({
                    "disc_number": 1,
                    "track_number": track.get("position", "0"),
                    "cancion": track["title"],
                    "interprete_cancion": data["artists"][0]["name"],
                    "cancion_url": None
                })
        
        return canciones

    return []

# 📌 Guardar CD en la base de datos
def guardar_cd_en_bd(numero_cd, titulo_cd, autor, datos_cd):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
    INSERT INTO fonoteca_cd (numero_cd, titulo_cd, autor, id_cd, carátula_cd, genero_musical)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    valores = (numero_cd, titulo_cd, autor, datos_cd["id_cd"], datos_cd["carátula_cd"], datos_cd["genero_musical"])
    
    cursor.execute(query, valores)
    cd_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return cd_id

# 📌 Guardar canciones en la base de datos
def guardar_canciones_en_bd(id_cd, canciones):
    if not canciones:
        print("⚠ No hay canciones para guardar en la BD.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for cancion in canciones:
        query = """
        INSERT INTO fonoteca_canciones (id, disc_number, track_number, cancion, interprete_cancion, cancion_url)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        valores = (id_cd, cancion["disc_number"], cancion["track_number"], cancion["cancion"], cancion["interprete_cancion"], cancion["cancion_url"])
        
        cursor.execute(query, valores)
    
    conn.commit()
    conn.close()

    print(f"💾 {len(canciones)} canciones añadidas correctamente a la BD.")

# 📌 Configurar Streamlit
st.title("Añadir Nuevo CD a la Fonoteca")

# 📌 Formulario de entrada
numero_cd = st.text_input("Número del CD")
autor = st.text_input("Autor")
titulo_cd = st.text_input("Título del CD")

if st.button("Buscar y Guardar CD"):
    token_spotify = obtener_token_spotify()
    datos_cd = buscar_en_spotify(titulo_cd, autor, token_spotify) or buscar_en_discogs(titulo_cd, autor)

    if datos_cd:
        st.success(f"✅ CD encontrado: {titulo_cd} - {autor}")

        if datos_cd["carátula_cd"]:
            st.image(datos_cd["carátula_cd"], width=300, caption="Carátula del CD")
        
        st.write(f"🎵 **Género:** {datos_cd['genero_musical']}")

        cd_id = guardar_cd_en_bd(numero_cd, titulo_cd, autor, datos_cd)

        # 🔹 Buscar canciones en Spotify o Discogs
        canciones = buscar_canciones_spotify(datos_cd["id_cd"], token_spotify) or buscar_canciones_discogs(datos_cd["id_cd"])

        if canciones:
            guardar_canciones_en_bd(cd_id, canciones)
            st.success(f"🎵 {len(canciones)} canciones añadidas correctamente")
        else:
            st.warning("⚠ No se encontraron canciones en Spotify ni Discogs.")

    else:
        st.error("❌ No se encontró el CD en Spotify ni en Discogs.")