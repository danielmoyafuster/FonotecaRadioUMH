import sqlite3

# Ruta de la base de datos
db_path = "./db/FonotecaRadioUMH.db"

# Lista de canciones a insertar (track_number, interprete_cancion, cancion)
canciones_a_insertar = [
    (287,1,1,"Añoranza","Sin saber por que"),
    (287,1,2,"Añoranza","Según pasa el tiempo"),
    (287,1,3,"Añoranza","Armonía perdida"),
    (287,1,4,"Añoranza","Vivo por vivir"),
    (287,1,5,"Añoranza","Recuerdos"),
    (287,1,6,"Añoranza","Dias sin retorno"),
    (287,1,7,"Añoranza","Yo y mi sombra"),
    (287,1,8,"Añoranza","Un día brumoso"),
    (287,1,9,"Añoranza","Recuerda"),
    (287,1,10,"Añoranza","Susurrando"),
    (287,1,11,"Añoranza","El silencio"),
    (287,1,12,"Añoranza","Noche y día"),
    (287,1,13,"Añoranza","Volver a empezar"),
    (287,1,14,"Añoranza", "El sueño imposible"),
    (287,1,15,"Añoranza", "Yo creo"),
    (287,1,16,"Añoranza", "Esta noche pasará"),
    (287,1,17,"Añoranza", "Adiós tristeza"),
    (287,1,18,"Añoranza", "Házmelo creer"),
    (287,1,19,"Añoranza", "Como en viejos tiempos"),
    (287,1,20,"Añoranza", "Con una canción en mi corazón"),
    (287,1,21,"Añoranza", "Un poco de paz")



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