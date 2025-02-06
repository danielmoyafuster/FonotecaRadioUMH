import sqlite3
import os

# 📌 Ruta de la base de datos
DB_PATH = "./db/FonotecaRadioUMH.db"

# 📌 Ruta de la carpeta de imágenes
IMAGES_PATH = "./imagenes_cd/"

# 📌 Conectar a la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 📌 Buscar imágenes en la carpeta y actualizar la base de datos
for filename in os.listdir(IMAGES_PATH):
    print(filename)
    if filename.startswith("cd_") and filename.endswith(".jpg"):
        try:
            # 🔹 Extraer el ID del archivo (CD_[número].jpg → número)
            cd_id = filename.split("_")[1].split(".")[0]

            # 🔹 Ruta completa de la imagen
            image_path = os.path.join(IMAGES_PATH, filename)
            print(cd_id)
            # 🔹 Actualizar la base de datos con la carátula correcta
            cursor.execute("UPDATE fonoteca_cd SET carátula_cd = ? WHERE id = ?", (image_path, cd_id))

        except Exception as e:
            print(f"⚠️ Error con {filename}: {e}")

# 📌 Guardar cambios y cerrar conexión
conn.commit()
conn.close()

print("✅ Carátulas restauradas correctamente desde `/imagenes_cd/`.")