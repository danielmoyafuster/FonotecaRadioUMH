import requests
import base64


# Configurar credenciales de Spotify
SPOTIFY_CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
SPOTIFY_CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"
# Track ID de una canción de la fonoteca (extraído de cancion_url)
TRACK_ID = "6vXZs9rEQF7Nd6O8Ue7NrT"  # Sustituye con un track ID real de la base de datos

 Función para obtener el token de acceso de Spotify
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
    else:
        print(f"⚠ Error en la API de Spotify: {response.status_code} - {response.text}")
        return None

# Obtener token de Spotify
token_spotify = obtener_token_spotify()

if token_spotify:
    # Obtener datos de la canción
    audio_features = obtener_audio_features(TRACK_ID, token_spotify)
    
    # Mostrar los resultados
    print("🎵 Características de audio:", audio_features)