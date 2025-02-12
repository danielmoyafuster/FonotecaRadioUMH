import sqlite3
import requests
import base64
from tqdm import tqdm  # Barra de progreso


# 📌 Credenciales de Spotify
SPOTIFY_CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
SPOTIFY_CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"


# Ruta de la base de datos SQLite
DB_PATH = "/Users/danielmoyafuster/FonotecaRadioUMH/db/FonotecaRadioUMH.db"

# Función para obtener el token de acceso de Spotify
def obtener_token_spotify():
    url = "https://accounts.spotify.com/api/token"
    credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    credentials_b64 = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {credentials_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"⚠ Error al obtener el token: {response.status_code} - {response.text}")
        return None

# Función para obtener las características de audio de una canción en Spotify
def obtener_audio_features(track_id, token):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()  # Devuelve las características de audio
    return None

# Conectar a la base de datos y obtener las canciones con `cancion_url`
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT id, cancion_url FROM fonoteca_canciones WHERE cancion_url IS NOT NULL AND danceability IS NULL;")
canciones = cursor.fetchall()  # Lista de canciones a analizar

# Obtener el token de acceso de Spotify
token_spotify = obtener_token_spotify()

if token_spotify:
    print(f"🔍 Encontradas {len(canciones)} canciones sin análisis de audio. Iniciando actualización...\n")

    for song_id, song_url in tqdm(canciones, desc="Analizando canciones", unit="canción"):
        track_id = song_url.split("/")[-1].split("?")[0]  # Extraer el track ID de la URL

        audio_features = obtener_audio_features(track_id, token_spotify)

        if audio_features:
            # Extraer los valores obtenidos
            danceability = audio_features.get("danceability")
            energy = audio_features.get("energy")
            valence = audio_features.get("valence")
            tempo = audio_features.get("tempo")
            instrumentalness = audio_features.get("instrumentalness")
            speechiness = audio_features.get("speechiness")
            acousticness = audio_features.get("acousticness")

            # Actualizar la base de datos con los valores obtenidos
            cursor.execute("""
                UPDATE fonoteca_canciones 
                SET danceability = ?, energy = ?, valence = ?, tempo = ?, 
                    instrumentalness = ?, speechiness = ?, acousticness = ?
                WHERE id = ?;
            """, (danceability, energy, valence, tempo, instrumentalness, speechiness, acousticness, song_id))

    conn.commit()
    print("\n✔ Actualización completada con éxito.")
else:
    print("⚠ No se pudo obtener el token de Spotify.")

# Cerrar conexión con la base de datos
conn.close()