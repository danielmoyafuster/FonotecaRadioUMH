import sqlite3

# Ruta de la base de datos
db_path = "./db/FonotecaRadioUMH.db"

# Lista de canciones a insertar (track_number, interprete_cancion, cancion)
canciones_a_insertar = [

(364,1,1,"The Jayhawks","Two Angels"),
(364,1,2,"The Jayhawks","Ain't No End"),
(364,1,3,"The Jayhawks","Waiting For The Sun"),
(364,1,4,"The Jayhawks","Martin's Song"),
(364,1,5,"The Jayhawks","Clouds"),
(364,1,6,"The Jayhawks","Settled Down Like Rain"),
(364,1,7,"The Jayhawks","Blue"),
(364,1,8,"The Jayhawks","I'd Run Away"),
(364,1,9,"The Jayhawks","Over My Shoulder"),
(364,1,10,"The Jayhawks","Miss Williams' Guitar"),
(364,1,11,"The Jayhawks","Trouble"),
(364,1,12,"The Jayhawks","Big Star"),
(364,1,13,"The Jayhawks","The Man Who Loved Life"),
(364,1,14,"The Jayhawks","Smile"),
(364,1,15,"The Jayhawks","I'm Gonna Make You Love Me"),
(364,1,16,"The Jayhawks","What Led Me To This Town"),
(364,1,17,"The Jayhawks","Tailspin"),
(364,1,18,"The Jayhawks","All The Right Reasons"),
(364,1,19,"The Jayhawks","Save It For A Rainy Day"),
(364,1,20,"The Jayhawks","Angelyne"),
(364,2,1,"The Jayhawks","Falling Star"),
(364,2,2,"The Jayhawks","Old Woman From Red Clay"),
(364,2,3,"The Jayhawks","That's The Bag I'm In"),
(364,2,4,"The Jayhawks","Won't Be Coming Home"),
(364,2,5,"The Jayhawks","Stone Cold Mess"),
(364,2,6,"The Jayhawks","Mission On 2nd"),
(364,2,7,"The Jayhawks","Lights"),
(364,2,8,"The Jayhawks","Darling Today"),
(364,2,9,"The Jayhawks","Break My Mind"),
(364,2,10,"The Jayhawks","Get The Load Out"),
(364,2,11,"The Jayhawks","Poor Little Fish (Early Version)"),
(364,2,12,"The Jayhawks","Someone Will"),
(364,2,13,"The Jayhawks","Cure For This"),
(364,2,14,"The Jayhawks","I Can Make It On My Own"),
(364,2,15,"The Jayhawks","Rotterdam"),
(364,2,16,"The Jayhawks","Follow Me"),
(364,2,17,"The Jayhawks","In The Canyon"),
(364,2,18,"The Jayhawks","Tailspin (Early Version)"),
(364,2,19,"The Jayhawks","I Think I've Had Enough"),
(364,2,20,"The Jayhawks","Help Me Forget"),
(364,3,1,"The Jayhawks","Waiting For The Sun"),
(364,3,2,"The Jayhawks","Take Me With You (When You Go)"),
(364,3,3,"The Jayhawks","Settled Down Like Rain"),
(364,3,4,"The Jayhawks","Hollywood Town Hall EPK"),
(364,3,5,"The Jayhawks","Blue"),
(364,3,6,"The Jayhawks","I'd Run Away"),
(364,3,7,"The Jayhawks","Big Star")




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