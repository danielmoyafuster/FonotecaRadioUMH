import sqlite3
import requests
from tqdm import tqdm  # 📊 Barra de progreso
import base64


# ⚡ Tu Client ID y Client Secret de Spotify (debes generarlos en https://developer.spotify.com)

SPOTIFY_CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
SPOTIFY_CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"



# Ruta de la base de datos SQLite
DB_PATH = "/Users/danielmoyafuster/FonotecaRadioUMH/db/FonotecaRadioUMH.db"

# Función para obtener el token de acceso de Spotify
def obtener_token_spotify():
    """Solicita un token de acceso a la API de Spotify."""
    url = "https://accounts.spotify.com/api/token"
    
    # Codificar credenciales en Base64
    credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    credentials_b64 = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {credentials_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"grant_type": "client_credentials"}

    # Enviar solicitud a Spotify
    response = requests.post(url, headers=headers, data=data)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"⚠ Error al obtener el token: {response.status_code} - {response.text}")
        return None
        
# Función para obtener el `release_date` del álbum de una canción en Spotify
def obtener_album_release_date(track_url, token):
    track_id = track_url.split("/")[-1].split("?")[0]  # Extraer el ID de la canción desde la URL de Spotify
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["album"]["release_date"]  # Extraer la fecha de lanzamiento
    return None

# Conectar a la base de datos y obtener canciones con `cancion_url`
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT id, cancion_url FROM fonoteca_canciones WHERE cancion_url IS NOT NULL AND album_release_date IS NULL;")
canciones = cursor.fetchall()  # Lista de canciones a actualizar

# Obtener token de Spotify
token_spotify = obtener_token_spotify()

if token_spotify:
    print(f"🔍 Encontradas {len(canciones)} canciones sin fecha de lanzamiento. Iniciando actualización...\n")

    for song_id, song_url in tqdm(canciones, desc="Actualizando canciones", unit="canción"):
        release_date = obtener_album_release_date(song_url, token_spotify)

        if release_date:
            # Actualizar la base de datos con la fecha obtenida
            cursor.execute("UPDATE fonoteca_canciones SET album_release_date = ? WHERE id = ?", (release_date, song_id))

    conn.commit()
    print("\n✔ Actualización completada con éxito.")
else:
    print("⚠ No se pudo obtener el token de Spotify.")

# Cerrar conexión con la base de datos
conn.close()