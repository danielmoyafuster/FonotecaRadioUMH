import requests
import re
import sqlite3

# 📌 Ruta de la base de datos SQLite
DB_PATH = "./db/FonotecaRadioUMH.db"

class DiscogsExtractor:
    BASE_URL = "https://api.discogs.com/releases/"

    def __init__(self, release_id):
        self.release_id = release_id
        self.data = None

    def fetch_data(self):
        """Obtiene los datos del lanzamiento desde la API de Discogs"""
        url = f"{self.BASE_URL}{self.release_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            self.data = response.json()
        else:
            raise Exception(f"Error al obtener datos de Discogs: {response.status_code}")

    def get_album_title(self):
        """Obtiene el nombre del disco"""
        if not self.data:
            self.fetch_data()
        return self.data.get("title", "Título desconocido")

    def get_album_cover_url(self):
        """Obtiene la URL de la carátula del disco"""
        if not self.data:
            self.fetch_data()
        
        images = self.data.get("images", [])
        if images:
            return images[0].get("uri", None)  # URL de la carátula principal
        return None  # No hay carátula disponible

    def parse_disc_number(self, position):
        """Extrae el número de disco desde la posición (ej: '2-01' → disco 2)"""
        if position:
            match = re.match(r"(\d+)-\d+", position)  # Buscar patrón "2-01"
            if match:
                return int(match.group(1))  # Devuelve el número antes del guion
        return 1  # Si no hay información, asumimos que es el disco 1

    def extract_tracks(self):
        """Extrae la información de cada pista: disc_number, track_number, interprete_cancion, cancion"""
        if not self.data:
            self.fetch_data()

        tracklist = self.data.get("tracklist", [])
        extracted_tracks = []

        for track in tracklist:
            position = track.get("position", "")  # Posición en formato "1-01", "2-02", etc.
            disc_number = self.parse_disc_number(position)
            track_number = int(position.split("-")[-1]) if "-" in position else int(position) if position.isdigit() else None
            cancion = track.get("title", "Desconocido")

            # Obtener el intérprete principal
            if "artists" in track and track["artists"]:
                interprete_cancion = ", ".join([artist["name"] for artist in track["artists"]])
            else:
                interprete_cancion = "Desconocido"

            extracted_tracks.append({
                "disc_number": disc_number,
                "track_number": track_number if track_number is not None else len(extracted_tracks) + 1,
                "interprete_cancion": interprete_cancion,
                "cancion": cancion
            })

        return extracted_tracks


def actualizar_caratula_en_bd(cd_id, cover_url):
    """Actualiza la tabla fonoteca_cd con la URL de la carátula"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE fonoteca_cd SET "carátula_cd" = ? WHERE id = ?
    """, (cover_url, cd_id))  # ✅ Usamos "carátula_cd" con tilde

    conn.commit()
    conn.close()
    print(f"✅ Carátula actualizada en la base de datos con la URL: {cover_url}")


def insertar_en_base_de_datos(cd_id, tracks):
    """Inserta las canciones en la tabla fonoteca_canciones"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for track in tracks:
        cursor.execute("""
            INSERT INTO fonoteca_canciones (id, disc_number, track_number, interprete_cancion, cancion)
            VALUES (?, ?, ?, ?, ?)
        """, (cd_id, track["disc_number"], track["track_number"], track["interprete_cancion"], track["cancion"]))

    conn.commit()
    conn.close()
    print(f"✅ {len(tracks)} canciones añadidas a la fonoteca con ID de disco {cd_id}.")


# 🔹 Pedir los IDs al usuario
if __name__ == "__main__":
    release_id = input("Introduce el ID del lanzamiento de Discogs: ").strip()
    cd_id = input("Introduce el ID del disco en la tabla fonoteca_cd: ").strip()

    if release_id.isdigit() and cd_id.isdigit():
        extractor = DiscogsExtractor(int(release_id))
        album_title = extractor.get_album_title()  # Obtener el nombre del disco
        cover_url = extractor.get_album_cover_url()  # Obtener la URL de la carátula
        tracks = extractor.extract_tracks()  # Obtener las canciones

        print(f"\n📀 Álbum: {album_title}\n")
        print(f"🖼️ Carátula: {cover_url}\n" if cover_url else "❌ No hay carátula disponible.\n")
        print("🎵 Lista de canciones extraídas:\n")
        for track in tracks:
            print(f"Disco {track['disc_number']}, Pista {track['track_number']}: {track['interprete_cancion']} - {track['cancion']}")

        # Confirmar si queremos guardar la información
        confirmar = input("\n¿Quieres guardar estas canciones y actualizar la carátula en la base de datos? (s/n): ").strip().lower()
        if confirmar == "s":
            # Actualizar la URL de la carátula en la base de datos
            if cover_url:
                actualizar_caratula_en_bd(int(cd_id), cover_url)

            # Insertar los datos en la base de datos
            insertar_en_base_de_datos(int(cd_id), tracks)
        else:
            print("❌ Operación cancelada.")

    else:
        print("❌ Error: Ambos IDs deben ser números válidos.")