
# .-.-.-.-.-.-..-.-.-.-.-.-.-.-.-.-.-.--.-.-.-.-.-.-.-.-.-.-.-.-.-..-.-.-.-.-.-.-.-.-.-.-.--.-.-.-.-.-.-.-.-.-.-.-.-.-.
# DgsCanciones.py    V 2.0 06-02-2025 14:45
# extraer canciones de la api de Discogs
# datos de entrada :
# Introduce el ID del lanzamiento de Discogs: 1505060
# tomar el código de la url justo a continuación de release:
# p.ej. : https://www.discogs.com/es/release/1505060-Various-Superventas-2007?srsltid=AfmBOorImE_n8qFBjOcqgf3FKwNonlphMB5t5u8-YdpEh_tQhtOzut89
#  aquí sería 1505060
#
# Introduce el ID del disco en la tabla fonoteca_cd: [el id del disco en fonoteca_cd
#
# .-.-.-.-.-.-..-.-.-.-.-.-.-.-.-.-.-.--.-.-.-.-.-.-.-.-.-.-.-.-.-..-.-.-.-.-.-.-.-.-.-.-.--.-.-.-.-.-.-.-.-.-.-.-.-.-.
import sqlite3
import requests
import re  # Para procesar números de disco correctamente
import os  # Para manejar archivos y rutas

class DiscogsExtractor:
    def __init__(self, release_id, token, db_cd_id):
        """
        Inicializa el extractor con el ID del lanzamiento de Discogs,
        el token de autenticación y el ID del disco en la base de datos.
        """
        self.release_id = release_id
        self.token = token
        self.db_cd_id = db_cd_id
        self.release_data = self.get_release_data()

    def get_release_data(self):
        """
        Obtiene los datos del lanzamiento desde la API de Discogs.
        """
        url = f"https://api.discogs.com/releases/{self.release_id}"
        headers = {"Authorization": f"Discogs token={self.token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al obtener datos de Discogs: {response.status_code}")
            return None

    def extract_tracks(self):
        """
        Extrae las pistas del lanzamiento de Discogs y limpia los datos.
        Si una pista no tiene intérprete, usa el artista principal del álbum.
        """
        if not self.release_data:
            print("⚠️ No se pudieron obtener los datos del lanzamiento.")
            return []

        # 🔹 Obtener el artista principal del álbum
        album_artist = self.release_data.get("artists", [{}])[0].get("name", "Desconocido")
    
        tracks = []

        for track in self.release_data.get('tracklist', []):
            position = track.get('position', '').strip()
            title = track.get('title', '').strip()
            artists = track.get('artists', [])

            # ✅ Si la pista no tiene artistas, usar el artista del álbum
            interprete = ", ".join([artist['name'] for artist in artists]) if artists else album_artist

            # 🔹 **LIMPIEZA DEL INTERPRETE**
            interprete = re.sub(r'\*$', '', interprete).strip()  # Eliminar "*" al final
            interprete = re.sub(r'\s*\(\d+\)', '', interprete).strip()  # Eliminar paréntesis con números
            
            # Extraer número de disco y pista
            disc_number, track_number = self.get_disc_and_track_number(position)

            # ❌ Ignorar DVDs
            if disc_number is None or track_number is None:
                continue  

            tracks.append({
                "disc_number": disc_number,
                "track_number": track_number,
                "interprete": interprete,
                "title": title
            })

        return tracks

    def get_disc_and_track_number(self, position):
        """
        Extrae correctamente el número de disco y pista de la posición.
        Si la pista pertenece a un DVD, **se ignora**.
        """
        if not position:
            return None, None

        if "-" in position:
            parts = position.split("-")
            disc_part = parts[0].upper()
            track_part = parts[-1]
        else:
            disc_part = "CD1"  
            track_part = position

        if "DVD" in disc_part:
            return None, None  

        disc_match = re.search(r'\d+', disc_part)
        disc_number = int(disc_match.group()) if disc_match else 1

        track_match = re.search(r'\d+', track_part)
        track_number = int(track_match.group()) if track_match else None

        return disc_number, track_number

    def save_tracks_to_db(self, db_path):
        """
        Guarda las canciones en la base de datos SQLite.
        """
        tracks = self.extract_tracks()
        if not tracks:
            print("❌ No hay canciones para guardar.")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for track in tracks:
            disc_number = track["disc_number"]
            track_number = track["track_number"]
            interprete = track["interprete"]
            title = track["title"]

            cursor.execute("""
                SELECT Id FROM fonoteca_canciones 
                WHERE Id = ? AND disc_number = ? AND track_number = ? AND cancion = ? AND interprete_cancion = ?
            """, (self.db_cd_id, disc_number, track_number, title, interprete))

            exists = cursor.fetchone()

            if not exists:
                cursor.execute("""
                    INSERT INTO fonoteca_canciones (Id, disc_number, track_number, interprete_cancion, cancion) 
                    VALUES (?, ?, ?, ?, ?)
                """, (self.db_cd_id, disc_number, track_number, interprete, title))
                print(f"✅ Añadida: Disco {disc_number}, Pista {track_number} → {interprete} - {title}")
            else:
                print(f"⚠️ Ya existe: Disco {disc_number}, Pista {track_number} → {interprete} - {title}")

        conn.commit()
        conn.close()
        print("\n✅ Guardado completado en la base de datos.")

# 🔹 **Ejecución del código**
if __name__ == "__main__":
    release_id = input("Introduce el ID del lanzamiento de Discogs: ")
    db_cd_id = input("Introduce el ID del disco en la tabla fonoteca_cd: ")

    TOKEN = "TU_TOKEN_AQUI"
    DB_PATH = "./db/FonotecaRadioUMH.db"

    extractor = DiscogsExtractor(release_id, TOKEN, db_cd_id)
    extractor.save_tracks_to_db(DB_PATH)