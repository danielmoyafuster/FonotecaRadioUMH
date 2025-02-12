import sqlite3

# Ruta de la base de datos
db_path = "./db/FonotecaRadioUMH.db"

# Lista de canciones a insertar (track_number, interprete_cancion, cancion)
canciones_a_insertar = [

(778,1,1,"-","Memorias de África"),
(778,1,2,"-","La traviata"),
(778,1,3,"-","2001 una Odiseadel Espacio"),
(778,1,4,"-","Gorky Park"),
(778,1,5,"-","Muerte en Venecia"),
(778,1,6,"-","Apocalipse Now"),
(778,1,7,"-","Misery"),
(778,1,8,"-","Volver a empezar"),
(778,1,9,"-","Durmiendo con su enemigo"),
(778,1,10,"-","Las brujas de Eastwick")




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