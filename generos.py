import sqlite3
import requests
import time  # Para animar la barra de progreso
from tqdm import tqdm  # Biblioteca para la barra de progreso

# 🔹 REEMPLAZA ESTOS DATOS CON TU CLIENT ID Y CLIENT SECRET DE SPOTIFY
# Configurar credenciales de Spotify
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"


DB_PATH = "./db/FonotecaRadioUMH.db"

def get_spotify_token():
    """
    Obtiene un token de acceso a la API de Spotify.
    """
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_album_genre(album_id, token):
    """
    Obtiene el género musical de un álbum en Spotify usando `id_cd`.
    """
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        album_data = response.json()
        genres = album_data.get("genres", [])
        return ", ".join(genres) if genres else None  # Devuelve una cadena con los géneros o None
    return None

def get_artist_genre(artist_name, token):
    """
    Busca un artista en Spotify y obtiene su género musical si el álbum no lo tiene.
    """
    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        artists = data.get("artists", {}).get("items", [])
        if artists:
            return ", ".join(artists[0].get("genres", [])) or None
    return None

def get_albums_from_db():
    """
    Obtiene los registros de la tabla `fonoteca_cd` donde `id_cd` tenga valor.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT Id, id_cd, autor FROM fonoteca_cd WHERE id_cd IS NOT NULL AND genero_musical IS NULL")
    albums = cursor.fetchall()

    conn.close()
    return albums

def update_album_genre(album_id, genre):
    """
    Actualiza el campo `genero_musical` en la base de datos para un álbum específico.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("UPDATE fonoteca_cd SET genero_musical = ? WHERE Id = ?", (genre, album_id))
    conn.commit()
    conn.close()

def main():
    """
    Obtiene el género de los álbumes en Spotify y actualiza la base de datos.
    """
    token = get_spotify_token()
    if not token:
        return

    albums = get_albums_from_db()
    if not albums:
        return

    # Barra de progreso
    for album in tqdm(albums, desc="Actualizando géneros", unit=" álbum", ncols=100):
        album_id, spotify_album_id, author = album
        genre = get_album_genre(spotify_album_id, token)

        if not genre:  # Si no hay género en el álbum, buscar el del artista
            genre = get_artist_genre(author, token)

        if genre:
            update_album_genre(album_id, genre)

        time.sleep(0.5)  # Pausa para evitar bloqueos de la API

if __name__ == "__main__":
    main()