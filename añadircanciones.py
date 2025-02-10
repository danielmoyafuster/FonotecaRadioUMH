import sqlite3

# Ruta de la base de datos
db_path = "./db/FonotecaRadioUMH.db"

# Lista de canciones a insertar (track_number, interprete_cancion, cancion)
canciones_a_insertar = [

(846,1,1,"Desplante","Kalash in (con DJ Joaking)"),
(846,1,2,"Desplante","Aunque les duela [Producido por DJ Joaking]"),
(846,1,3,"Desplante","Frustrados (con La Demente Eme) [Producido por Rigor Mortis]"),
(846,1,4,"Desplante","Silencio (con Neura) [Producido por Soma]"),
(846,1,5,"Desplante","Vida rap ida (con ZPU y Nach) [Producido por Soma]"),
(846,1,6,"Desplante","Llamalo X [Producido por Soma]"),
(846,1,7,"Desplante","IBZ (con Del valle) [Producido por Gorka]"),
(846,1,8,"Desplante","Adelante [Producido por Rigor Mortis]"),
(846,1,9,"Desplante","Miedo al miedo (con Diana Feria) [Producido por Soma]"),
(846,1,10,"Desplante","Pompas de jabon (con Neura y Diana Feria) [Producido por Soma]"),
(846,1,11,"Desplante","Antiopresion (con Dj Chavez) [Producido por Soma]"),
(846,1,12,"Desplante","Outro -Producido por AsesYNato-")



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
                (id_disco,disc_number, track_number, interprete,cancion)
            )

        conn.commit()
        print("✅ Canciones añadidas correctamente.")
    except sqlite3.Error as e:
        print(f"❌ Error al insertar las canciones: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    insertar_canciones()