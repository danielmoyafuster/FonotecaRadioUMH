import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm

# Configurar credenciales de Spotify
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"  # Reemplaza con tu Client ID
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"  # Reemplaza con tu Client Secret

# Autenticación con Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

def obtener_informacion_cancion(track_id):
    """
    Obtiene toda la información posible de una canción utilizando el ID de Spotify.
    """
    try:
        track_info = sp.track(track_id)
        return {
            "ID": track_info["id"],
            "Nombre Canción": track_info["name"],
            "Artistas": ", ".join(artist["name"] for artist in track_info["artists"]),
            "Álbum": track_info["album"]["name"],
            "Popularidad": track_info["popularity"],
            "Duración (ms)": track_info["duration_ms"],
            "Explícita": track_info["explicit"],
            "Fecha de Lanzamiento": track_info["album"]["release_date"],
            "Enlace Spotify": track_info["external_urls"]["spotify"],
            "Vista Previa URL": track_info["preview_url"],
        }
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error al obtener información para la canción con ID {track_id}: {e}")
        return {
            "ID": track_id,
            "Nombre Canción": "No disponible",
            "Artistas": "No disponible",
            "Álbum": "No disponible",
            "Popularidad": "No disponible",
            "Duración (ms)": "No disponible",
            "Explícita": "No disponible",
            "Fecha de Lanzamiento": "No disponible",
            "Enlace Spotify": "No disponible",
            "Vista Previa URL": "No disponible",
        }

def procesar_excel(input_excel_path, output_excel_path):
    """
    Procesa el archivo Excel y obtiene información de Spotify para cada ID de canción
    siempre y cuando el ID no sea "No disponible".
    """
    try:
        # Leer el archivo Excel
        df = pd.read_excel(input_excel_path)
        
        if "ID" not in df.columns:
            print("El archivo Excel no contiene la columna 'ID'.")
            return
        
        # Filtrar los IDs válidos (excluyendo "No disponible")
        ids_validos = df["ID"].dropna().unique()
        ids_validos = [track_id for track_id in ids_validos if track_id != "No disponible"]
        
        # Inicializar una lista para almacenar la información de las canciones
        canciones_info = []

        # Progresar sobre cada ID válido
        for track_id in tqdm(ids_validos, desc="Procesando IDs de canciones"):
            info = obtener_informacion_cancion(track_id)
            canciones_info.append(info)

        # Crear un DataFrame con la información obtenida
        output_df = pd.DataFrame(canciones_info)

        # Guardar en un nuevo archivo Excel
        output_df.to_excel(output_excel_path, index=False)
        print(f"Información de las canciones guardada en: {output_excel_path}")
    except Exception as e:
        print(f"Error al procesar el archivo Excel: {e}")

# Rutas del archivo de entrada y salida
input_excel_path = "FONOTECA_CD_UMH_SPOTIFY.xlsx"  # Archivo de entrada
output_excel_path = "FONOTECA_CD_UMH_SPOTIFY_DETALLES.xlsx"  # Archivo de salida

# Ejecutar la función
procesar_excel(input_excel_path, output_excel_path)