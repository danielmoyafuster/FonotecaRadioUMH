import sqlite3

# Ruta de la base de datos
db_path = "./db/FonotecaRadioUMH.db"

# Lista de correcciones (interprete_cancion, cancion, nuevo_disc_number, nuevo_track_number)
correcciones = [
("Los Enemigos", "Soy Un Ser Humano", 2,1),
("Los Enemigos", "Un Tio Cabal",2,2),
("Los Enemigos", "Sanchidrian",2,3),
("Los Enemigos", "Boquerón",2,4),
("Los Enemigos", "No Protejas",2,5),
("Los Enemigos", "Que Bien Me Lo Paso",2,6),
("Los Enemigos", "Yo, El Rey", 2,7),
("Los Enemigos", "John Wayne",2,8),
("Los Enemigos", "¿No Amanece En Bouzas? (Delirio Vigués)",2,9),
("Los Enemigos", "Afición",2,10),
("Los Enemigos", "El Gran Calambre Final",3,1),
("Los Enemigos", "El Fraile Y Yo",3,2),
("Los Enemigos", "Traspiés",3,3),
("Los Enemigos", "Ouija",3,4),
("Los Enemigos", "La Torre De Babel",3,5),
("Los Enemigos", "Paquito",3,6),
("Los Enemigos", "Desde El Jergón",3,7),
("Los Enemigos", "Septiembre",3,8),
("Los Enemigos", "Yo No Quiero Ser Feliz",3,9),
("Los Enemigos", "Miedo",3,10),
("Los Enemigos", "Firmarás",3,11),
("Los Enemigos", "Yo El Rey", 3,12),
("Los Enemigos", "Nadie Me Quiere",3,13)
]
def corregir_canciones():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for interprete, cancion, nuevo_disc, nuevo_track in correcciones:
            cursor.execute(
                """
                UPDATE fonoteca_canciones 
                SET disc_number = ?, track_number = ? 
                WHERE id = 173 AND interprete_cancion = ? AND cancion = ?
                """,
                (nuevo_disc, nuevo_track, interprete, cancion)
            )

        conn.commit()
        print("✅ Correcciones aplicadas correctamente.")
    except sqlite3.Error as e:
        print(f"❌ Error al actualizar la base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    corregir_canciones()