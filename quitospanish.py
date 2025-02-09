import sqlite3

# Ruta de la base de datos
db_path = "./db/FonotecaRadioUMH.db"

def corregir_titulos():
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Seleccionar canciones con id = 719 que contengan "-"
        cursor.execute("SELECT id, disc_number, track_number, cancion FROM fonoteca_canciones WHERE id = 897 AND cancion LIKE '%=%'")
        canciones = cursor.fetchall()

        # Si hay canciones para corregir
        if canciones:
            for id_cd, disc_number, track_number, titulo in canciones:
                nuevo_titulo = titulo.split("=")[-1].strip()  # Tomar solo la parte en inglés
                # Actualizar en la base de datos
                cursor.execute("""
                    UPDATE fonoteca_canciones 
                    SET cancion = ? 
                    WHERE id = ? AND disc_number = ? AND track_number = ?
                """, (nuevo_titulo, id_cd, disc_number, track_number))

            # Guardar cambios
            conn.commit()
            print(f"Se corrigieron {len(canciones)} títulos correctamente.")
        else:
            print("No se encontraron canciones para corregir.")

    except Exception as e:
        print("Error:", e)
    
    finally:
        conn.close()

# Ejecutar la corrección
corregir_titulos()