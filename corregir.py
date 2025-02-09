import sqlite3

# Ruta de la base de datos
db_path = "./db/FonotecaRadioUMH.db"

# Lista de correcciones (interprete_cancion, cancion, nuevo_disc_number, nuevo_track_number)
correcciones = [
    ("Arsenium", "Love Me..., Love Me...", 1, 1),
    ("Polinesia", "Aloha", 1, 2),
    ("Andy's Val Gourmet", "Chacarrón", 1, 3),
    ("Idem", "Voy Volando", 1, 4),
    ("Wisin Y Yandel", "En La Bailoteo", 1, 5),
    ("Xucro", "Mi Primera Vez", 1, 6),
    ("Baby Killa, Jimmy Bad Boy", "Dale Morena", 1, 7),
    ("Squeeze Up, Teishan, Rod Fame", "La Isla Bonita", 1, 8),
    ("David Bisbal", "Mami (Reggaeton Remix)", 1, 9),
    ("Safri Duo, Clark Anderson", "Ritmo De La Noche", 1, 10),
    ("Son De Sol", "Brujeria", 1, 11),
    ("Anabel Lee", "Miente Un Poco Mas Por Mi", 1, 12),
    ("Vaneese", "Bombóm", 1, 13),
    ("El Simbolo", "Pa' Delante Pa' Tras (De Reversa) (Summer 05 Mix)", 1, 14),
    ("Carlinhos Brown, DJ Dero", "Sambadream", 1, 15),
    ("Sonia Monroy", "Tu Eres Mi Cielo", 1, 16),
    ("Judiny, Aguakate, DJ Chucky", "Tu Bumper (Rmx)", 1, 17),
    ("Isabel Pantoja, Pumpin' Dolls", "Se Me Enamora El Alma", 1, 18),
    ("Adrián Leo", "Multiplica Ilusión", 1, 19),
    ("2 Dos Two", "Boom Boom", 1, 20),
    ("Papi Sanchez", "Enamorame", 2, 1),
    ("Nicky Jam, Rakim & Ken-Y", "Me Estoy Muriendo", 2, 2),
    ("Maria Isabel", "¡No Me Toques Las Palmas Que Me Conozco!", 2, 3),
    ("Don Omar", "Loba", 2, 4),
    ("at, Natalia", "I Love This Game", 2, 5),
    ("Flow Star", "Candela", 2, 6),
    ("Austin", "La Incondicional (XTM Reggaeton Remix)", 2, 7),
    ("Gusanito", "Xuku Xuku", 2, 8),
    ("Sara Martins", "Una Condición", 2, 9),
    ("Bimbo", "Amor Bandido", 2, 10),
    ("Beat Factory, Massiv 4", "Sugar Sugar", 2, 11),
    ("Schnappi", "Scchnappi (Kroko Italo Mix)", 2, 12),
    ("Massé", "Amor Brujo", 2, 13),
    ("David Velardo", "Reina De Mis Sueños", 2, 14),
    ("Santa Fe", "Que Baja Que Sube", 2, 15),
    ("Partypimpz, MC Miker G. & DJ Sven", "Holliday Rap 2005", 2, 16),
    ("Mash", "Be My Girl (Alex Andiamo Andiamo Radio)", 2, 17),
    ("DJ Chowuy", "Hasta Abajo Papi", 2, 18),
    ("Eddy Wata", "La Bomba", 2, 19),
    ("Bon Garçon", "Freek U", 3, 1),
    ("Studio B", "I See Girls (Tom Neville Mix)", 3, 2),
    ("Inaya Day", "Nasty Girl", 3, 3),
    ("Sunset Strippers", "Falling Stars (Radio Edit)", 3, 4),
    ("Dr. Kucho!, Pedro Del Moral", "Rain (I Want A Divorce)", 3, 5),
    ("Lil' Love", "Little Love", 3, 6),
    ("D.O.N.S., Technotronic", "Pump Up The Jam", 3, 7),
    ("Back To Basics, KTF", "Mamakossa (KTF Radio Edit)", 3, 8),
    ("Paco Pil", 'La Revolución "El Ritmo Maricón"', 3, 9),
    ("DJ Ross, Double You, J. & B.", "Get Up (On The Radio)", 3, 10),
    ("Paul Jackson", "Only One", 3, 11),
    ("DJ F", "Be My Lover Medley Pride (In The Name Of Love)", 3, 12),
    ("DJ Sammy", "Why?", 3, 13),
    ("On Line, Anqui", "Groovy Ride", 3, 14),
    ("Liza", "Maybe", 3, 15),
    ("Rhythm Addicts", "Kar.Na.Val", 3, 16),
    ("Shana Vanguarde", "Mamma Mia (Radio Edit)", 3, 17),
    ("TLM, Transvision Vamp", "Baby, I Don't Care 2005", 3, 18)
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
                WHERE id = 1007 AND interprete_cancion = ? AND cancion = ?
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