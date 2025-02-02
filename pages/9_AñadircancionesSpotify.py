import sqlite3
import requests
import time
from tqdm import tqdm  # Para la barra de progreso

# Configurar credenciales de Spotify
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

# Base de datos SQLite
DB_PATH = "./db/FonotecaRadioUMH.db"

# URL de autenticación de Spotify
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

def obtener_canciones_album(id_cd_spotify, token):
    """ Obtiene TODAS las canciones de un álbum en Spotify (maneja paginación correctamente) """
    url = f"https://api.spotify.com/v1/albums/{id_cd_spotify}/tracks?limit=50"
    headers = {"Authorization": f"Bearer {token}"}

    canciones = []
    
    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        for track in data.get("items", []):
            canciones.append({
                "disc_number": track["disc_number"],  
                "track_number": track["track_number"],  
                "interprete": track["artists"][0]["name"],  
                "cancion": track["name"],  
                "cancion_url": track["external_urls"]["spotify"] if "external_urls" in track else None
            })

        url = data.get("next")  # 🔹 Si hay más páginas, seguimos obteniendo más canciones
    
    return canciones

def importar_canciones():
    """ Obtiene los datos de los CDs con id_cd y busca sus canciones en Spotify """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 🔍 Obtener SOLO los CDs con id_cd
    cursor.execute("""
        SELECT id, id_cd 
        FROM fonoteca_cd
        WHERE id_cd IS NOT NULL AND id_cd != '';
    """)
    cds = cursor.fetchall()

    if not cds:
        print("✅ No hay CDs con id_cd en Spotify. Nada que importar.")
        conn.close()
        return

    # Obtener token de Spotify
    token = obtener_token_spotify()

    # Barra de progreso
    try:
        with tqdm(total=len(cds), desc="Obteniendo canciones de Spotify", unit=" CD") as pbar:
            for id_cd_local, id_cd_spotify in cds:
                canciones = obtener_canciones_album(id_cd_spotify, token)

                for cancion in canciones:
                    cursor.execute("""
                        INSERT INTO fonoteca_canciones (id, disc_number, interprete_cancion, track_number, cancion, cancion_url)
                        VALUES (?, ?, ?, ?, ?, ?);
                    """, (id_cd_local, cancion["disc_number"], cancion["interprete"], cancion["track_number"], cancion["cancion"], cancion["cancion_url"]))

                conn.commit()
                pbar.update(1)  
                time.sleep(0.5)  # Reducimos la pausa para acelerar el proceso

    except KeyboardInterrupt:
        print("\n⏸ Interrupción detectada. Guardando progreso y cerrando.")
    
    finally:
        conn.close()
        print("\n✅ Proceso finalizado correctamente.")

if __name__ == "__main__":
    importar_canciones()