import sqlite3

# Ruta de la base de datos
db_path = "./db/FonotecaRadioUMH.db"

# Lista de canciones a insertar (disc_number, track_number, interprete_cancion, cancion)
canciones_a_insertar = [

(5,1,"Gala","Freed From Desire"),
(5,2,"Eiffel 65","Blue [Da Ba Dee"),
(5,3,"Kate Ryan","Scream For More"),
(5,4, "Gigi D’Agostino","Your Love"),
(5,5, "ATB","9 PM [Till I Come]"),
(5,6, "Afrika Bambaataa","Just Get Up And Dance"),
(5,7, "Bus Stop Feat. Carl Douglas","Kung Fu Fighting"),
(5,8, "Jakatta", "American Dream"),
(5,9, "Candi Staton" , "Young Hearts Run Free 1999"),
(5,10, "Molella","If You Wanna Party"),
(5,11, "East Side Beat" , "Ride Like The Wind"),
(5,12, "Milk Inc." , "In My Eyes"),
(5,13, "Speed Limit", "Don’t Give Me Up"),
(5,14, "Prezioso Feat. Marvin", "Tell Me Why"),
(5,15, "Ice MC" , "Think About The Way"),
(5,16, "Ramirez","El Gallinero"),
(5,17, "Doop", "Doop"),
(5,18, "La Luna", "When The Morning Comes"),
(5,19, "Absolom", "Secret"),
(5,20, "Hermes House Band", "I Will Survive")
    
]

def insertar_canciones():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for disc_number, track_number, interprete, cancion in canciones_a_insertar:
            cursor.execute(
                """
                INSERT INTO fonoteca_canciones (id, disc_number, track_number, interprete_cancion, cancion)
                VALUES (?, ?, ?, ?, ?)
                """,
                (172, disc_number, track_number, interprete, cancion)
            )

        conn.commit()
        print("✅ Canciones añadidas correctamente a `fonoteca_canciones` con id = 172.")
    except sqlite3.Error as e:
        print(f"❌ Error al insertar las canciones: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    insertar_canciones()