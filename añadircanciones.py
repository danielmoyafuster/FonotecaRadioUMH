import sqlite3

# Ruta de la base de datos
db_path = "./db/FonotecaRadioUMH.db"

# Lista de canciones a insertar (track_number, interprete_cancion, cancion)
canciones_a_insertar = [

(1044,1,1,"Javier Abraldes","Vertical"),
(1044,1,2,"Thelonious Monk","Four in One"),
(1044,1,3,"Manuel Paino","Ao Abeiro"),
(1044,1,4,"John Coltrane","Like Sonny"),
(1044,1,5,"Narci Rodríguez","Day by Day"),
(1044,1,6,"Bill Evans","G Waltz"),
(1044,1,7,"Pablo Beloso","Penthagon"),
(1044,1,8,"Thelonious Monk","Five Spot Blues"),
(1044,1,9,"Pablo Beloso","Plaisanterie"),
(1044,1,10,"Pedro Freijeiro","In Three"),
(1044,1,11,"Bill Evans","Comrade Conrad"),
(1044,1,12,"Javier Abraldes","Ángeles"),
(1044,2,1,"Javier Abraldes","Tensegridad"),
(1044,2,2,"Bill Evans","Five"),
(1044,2,3,"Miguel Paz","Three Little Fishes"),
(1044,2,4,"McCoy Tyner","Blues on the Corner"),
(1044,2,5,"Valentin Caamaño","'Intro Certain' The Blind Wrestler"),
(1044,2,6,"Thelonious Monk","In walked Bud"),
(1044,2,7,"David Lojo","Terra de Goians"),
(1044,2,8,"Bill Evans","Loose Bloose"),
(1044,2,9,"Adrian Solla","Furatho"),
(1044,2,10,"Manuel Paino","Sen Medo"),
(1044,2,11,"Diego Vieito","Mr. Gestal"),
(1044,2,12,"David Mann","In the wee small hours of the morning"),
(1044,2,13,"Adrian Solla","Limited Time")




]   


def insertar_canciones():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for id_disco,disc_number, track_number, interprete, cancion in canciones_a_insertar:
            cursor.execute(
                """
                INSERT INTO fonoteca_canciones (id, disc_number, track_number, interprete_cancion, cancion)
                VALUES (?, ?, ?, ?, ?)
                """,
                (id_disco,disc_number, track_number, interprete, cancion)
            )

        conn.commit()
        print("✅ Canciones añadidas correctamente.")
    except sqlite3.Error as e:
        print(f"❌ Error al insertar las canciones: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    insertar_canciones()