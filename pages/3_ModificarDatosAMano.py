import streamlit as st
import sqlite3
import pandas as pd
import os
st.sidebar.title("Modificar Datos (Manual)")
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
        <a href="https://radio.umh.es/" target="_blank">
            <img src="https://radio.umh.es/files/2023/07/FOTO-PERFIL-RADIO.png" 
                 alt="Radio UMH" 
                 style="width: 150px; border-radius: 10px; margin-bottom: 10px;">
        </a>
        <p style="font-size: 16px; font-weight: bold; color: #333;">Gestión de la Fonoteca</p>
        <hr style="border: none; border-top: 1px solid #ccc; margin: 10px 0;">
    </div>
    """,
    unsafe_allow_html=True,
)

# Configurar título de la app
st.title("Actualizar Álbumes Manualmente")

# Definir la carpeta donde se guardarán las imágenes
IMAGENES_DIR = "./imagenes_cd"
os.makedirs(IMAGENES_DIR, exist_ok=True)

# Conectar a la base de datos SQLite
db_path = "FonotecaRadioUMH.db"
conn = sqlite3.connect(db_path)

# Obtener los CDs donde TÍTULO = "Álbum no encontrado"
query_albumes_no_encontrados = """
    SELECT DISTINCT autor, nombre_cd FROM fonoteca
    WHERE titulo = 'Álbum no encontrado' 
    AND nombre_cd IS NOT NULL 
    AND TRIM(nombre_cd) != ''
    ORDER BY autor, nombre_cd
"""
albumes_df = pd.read_sql_query(query_albumes_no_encontrados, conn)

# Cerrar conexión con la base de datos
conn.close()

# Contar el número de álbumes encontrados
num_albumes = len(albumes_df)

# Crear una lista de opciones en formato "AUTOR - NOMBRE CD"
if num_albumes > 0:
    albumes_df["combo_label"] = albumes_df["autor"] + " - " + albumes_df["nombre_cd"]
    album_dict = albumes_df.set_index("combo_label").to_dict("index")
    album_seleccionado_label = st.selectbox(f"Álbumes no encontrados en Spotify ({num_albumes}):", album_dict.keys())

    # Obtener datos del álbum seleccionado
    album_seleccionado = album_dict[album_seleccionado_label]["nombre_cd"]
    autor_seleccionado = album_dict[album_seleccionado_label]["autor"]

    # Subir la carátula manualmente
    st.subheader("Subir Carátula del CD")
    imagen_subida = st.file_uploader("📷 Sube la imagen de la carátula:", type=["jpg", "png", "jpeg"])
    
    if imagen_subida:
        # Guardar la imagen en la carpeta local
        imagen_path = os.path.join(IMAGENES_DIR, f"{album_seleccionado}.jpg")
        with open(imagen_path, "wb") as f:
            f.write(imagen_subida.read())
        st.success("✅ Carátula subida correctamente.")

    # Formulario para añadir canciones manualmente
    st.subheader("Agregar canciones manualmente")

    # Crear una lista para almacenar las canciones ingresadas
    canciones_ingresadas = []

    # Definir un número de canciones a ingresar
    num_canciones = st.number_input("¿Cuántas canciones tiene el álbum?", min_value=1, step=1)

    # Iterar y pedir información para cada canción
    for i in range(int(num_canciones)):
        st.write(f"🎵 Canción {i + 1}")
        numero_cancion = st.number_input(f"Número de pista {i + 1}:", min_value=1, step=1)
        autor_cancion = st.text_input(f"Autor de la canción {i + 1}:", key=f"autor_{i}")
        titulo_cancion = st.text_input(f"Título de la canción {i + 1}:", key=f"titulo_{i}")
        url_cancion = st.text_input(f"URL de la canción en otra plataforma (opcional) {i + 1}:", key=f"url_{i}")

        if numero_cancion and autor_cancion and titulo_cancion:
            canciones_ingresadas.append({
                "numero": numero_cancion,
                "autor": autor_cancion,
                "nombre_cd": album_seleccionado,
                "titulo": titulo_cancion,
                "url": url_cancion if url_cancion else "No disponible",
                "spotify_id": "No disponible",
                "imagen_url": imagen_path if imagen_subida else "No disponible"
            })

    # Botón para guardar los datos
    if st.button("💾 Guardar álbum y canciones"):
        if canciones_ingresadas:
            # Convertir la lista de canciones a DataFrame
            new_tracks_df = pd.DataFrame(canciones_ingresadas)

            # Conectar a SQLite para actualizar la base de datos
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Eliminar el registro antiguo con "Álbum no encontrado"
            cursor.execute("DELETE FROM fonoteca WHERE nombre_cd = ? AND autor = ?", (album_seleccionado, autor_seleccionado))
            conn.commit()

            # Insertar los nuevos datos en la base de datos
            new_tracks_df.to_sql("fonoteca", conn, if_exists="append", index=False)

            # Confirmar cambios y cerrar conexión
            conn.commit()
            conn.close()

            # Mensaje de éxito
            st.success(f"✅ El álbum '{album_seleccionado}' de {autor_seleccionado} ha sido actualizado manualmente.")
            
            if imagen_subida:
                st.image(imagen_path, caption="Nueva carátula del álbum", width=300)

else:
    st.write("✅ No hay álbumes sin encontrar en Spotify.")