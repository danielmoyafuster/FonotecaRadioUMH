import os
import time
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from tqdm import tqdm

# Configura las credenciales de Spotify
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

def search_album_songs_with_retries(author, album_name, retries=5):
    """
    Busca un álbum en Spotify y devuelve las canciones, URLs e IDs que contiene.
    Maneja automáticamente los límites de solicitudes usando `Retry-After`.
    """
    for attempt in range(retries):
        try:
            query = f"album:{album_name} artist:{author}"
            results = sp.search(q=query, type='album', limit=1)
            if results['albums']['items']:
                album_id = results['albums']['items'][0]['id']
                tracks = sp.album_tracks(album_id)['items']
                # Extraer nombre, URL y ID de cada canción
                return [
                    {
                        "name": track['name'],
                        "url": track['external_urls']['spotify'],
                        "id": track['id']
                    }
                    for track in tracks
                ]
            else:
                return [{"name": "Álbum no encontrado", "url": "No disponible", "id": "No disponible"}]
        except spotipy.exceptions.SpotifyException as e:
            # Manejar el límite de solicitudes usando `Retry-After`
            if "rate limit" in str(e):
                retry_after = int(e.headers.get("Retry-After", 5))  # Tiempo sugerido por la API
                print(f"Límite de solicitudes alcanzado. Esperando {retry_after} segundos...")
                time.sleep(retry_after)
            else:
                print(f"Error desconocido: {e}")
                break
    return [{"name": "Error al procesar", "url": "No disponible", "id": "No disponible"}]

def process_excel_with_validations_and_retries(input_excel_path, output_excel_path):
    """
    Procesa un archivo Excel para buscar canciones en Spotify con manejo de límites
    y extrae nombre, URL e ID de cada canción.
    """
    # Validar el archivo de entrada
    if not os.path.isfile(input_excel_path) or not input_excel_path.endswith((".xlsx", ".xls")):
        raise ValueError("El archivo de entrada no existe o no tiene una extensión válida (.xlsx, .xls).")

    try:
        df = pd.read_excel(input_excel_path)
        if "Nº" in df.columns and "AUTOR" in df.columns and "NOMBRE CD" in df.columns:
            tqdm.pandas(desc="Buscando canciones en Spotify")
            
            # Usar la función con reintentos para buscar canciones
            df['CANCIONES'] = df.progress_apply(
                lambda row: search_album_songs_with_retries(row['AUTOR'], row['NOMBRE CD']),
                axis=1
            )

            # Expandir los datos de las canciones en filas separadas
            exploded = df.explode('CANCIONES')
            exploded['TITULO'] = exploded['CANCIONES'].apply(lambda x: x['name'] if isinstance(x, dict) else None)
            exploded['URL'] = exploded['CANCIONES'].apply(lambda x: x['url'] if isinstance(x, dict) else None)
            exploded['ID'] = exploded['CANCIONES'].apply(lambda x: x['id'] if isinstance(x, dict) else None)

            # Eliminar la columna auxiliar
            exploded.drop(columns=['CANCIONES'], inplace=True)

            # Guardar el archivo actualizado
            exploded.to_excel(output_excel_path, index=False)
            print(f"Archivo procesado correctamente. Guardado en: {output_excel_path}")
        else:
            print("El archivo Excel no contiene las columnas requeridas: 'Nº', 'AUTOR', 'NOMBRE CD'.")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

# Rutas
input_excel_path = "FONOTECA_CD_UMH_UPDATED.xlsx"  # Asegúrate de que el archivo tenga extensión
output_excel_path = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

# Ejecutar
process_excel_with_validations_and_retries(input_excel_path, output_excel_path)