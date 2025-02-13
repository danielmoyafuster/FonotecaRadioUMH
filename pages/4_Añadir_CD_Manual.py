import streamlit as st
import sqlite3
import os
from PIL import Image
import requests

# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# 4_ActualizarDatosManual.py
# Añadir canciones a CD que no se encuentra en SPOTIFY
# Versión 2.0 05/02/2025 10:07
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.



#
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
st.sidebar.title("Añadir Canciones Manualmente")
st.sidebar.caption("Versión 2.0 05/02/2025 10:07")
st.markdown(
    '''
    <style>
        /* 🔹 Quitar bordes de la tabla */
        table {
            border-collapse: collapse;
            border: none;
            background: transparent;
            width: 100%;
        }

        /* 🔹 Quitar bordes y fondo de las celdas */
        th, td {
            border: none !important;
            background: transparent !important;
            padding: 10px;
        }

        /* 🔹 Ajustar tamaño y estilos de la imagen */
        .logo-container img {
            width: 180px;  /* Aumentamos un poco el tamaño */
            border-radius: 10px;
            transition: transform 0.2s;
        }

        /* 🔹 Efecto hover en la imagen */
        .logo-container img:hover {
            transform: scale(1.1); /* Hace que la imagen se agrande un poco al pasar el ratón */
        }

        /* 🔹 Centrar el título */
        .title-container h1 {
            color: #BD2830;
            text-align: center;
            font-size: 30px;
        }
    </style>

    <table>
        <tr>
            <th class="logo-container">
                <a href="https://radio.umh.es/" target="_blank">
                    <img src="https://radio.umh.es/files/2023/07/FOTO-PERFIL-RADIO.png" 
                         alt="Radio UMH">
                </a>
            </th>
            <th class="title-container">
                <h1>Consultar la Fonoteca</h1>
            </th>
        </tr>
    </table>
    ''',
    unsafe_allow_html=True,
)
#
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#
import streamlit as st
import sqlite3
import os
from PIL import Image
import requests

# 📌 Ruta de la base de datos SQLite y directorio de imágenes
DB_PATH = "./db/FonotecaRadioUMH.db"
IMAGES_DIR = "./imagenes_cd"

# 📌 Crear el directorio de imágenes si no existe
os.makedirs(IMAGES_DIR, exist_ok=True)

# 📌 Función para guardar la carátula
def guardar_caratula(id_cd, imagen):
    """ Guarda la carátula en la carpeta ./imagenes_cd con el formato cd_[id].jpg y actualiza la BD """
    if imagen is not None:
        ruta_imagen = os.path.join(IMAGES_DIR, f"cd_{id_cd}.jpg")
        
        # Guardar la imagen
        img = Image.open(imagen)
        img.save(ruta_imagen, format="JPEG")

        # Actualizar en la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE fonoteca_cd SET carátula_cd = ? WHERE id = ?", (ruta_imagen, id_cd))
        conn.commit()
        conn.close()
        
        return ruta_imagen
    return None

# 📌 Función para guardar canciones en la base de datos
def guardar_canciones(id_cd, canciones):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for cancion in canciones:
        cursor.execute("""
            INSERT INTO fonoteca_canciones (id, disc_number, track_number, interprete_cancion, cancion, cancion_url)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (id_cd, cancion["disc_number"], cancion["track_number"], cancion["interprete"], cancion["titulo"], cancion["url"]))

    conn.commit()
    conn.close()

# 📌 Obtener lista de CDs sin canciones
def obtener_cds_sin_canciones():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fc.id, fc.titulo_cd, fc.autor, fc.carátula_cd 
        FROM fonoteca_cd fc
        LEFT JOIN fonoteca_canciones fca ON fc.id = fca.id
        WHERE fca.id IS NULL
        GROUP BY fc.id;
    """)
    cds = cursor.fetchall()
    conn.close()
    return cds

# 📌 Interfaz de Streamlit
st.markdown("<h2 style='color: #BD2830; text-align: center;'>Añadir Canciones Manualmente</h2>", unsafe_allow_html=True)
st.write("Aquí puedes **seleccionar un CD sin canciones**, añadir canciones y subir una carátula manualmente.")

cds_sin_canciones = obtener_cds_sin_canciones()

if not cds_sin_canciones:
    st.success("✅ Todos los CDs tienen canciones. No hay nada que actualizar.")
else:
    opciones = {f"{titulo} - {autor}": id_cd for id_cd, titulo, autor, _ in cds_sin_canciones}
    seleccion = st.selectbox("Selecciona un CD sin canciones:", list(opciones.keys()))

    if seleccion:
        id_cd = opciones[seleccion]

        # 📌 Mostrar carátula si ya existe
        caratula_path = os.path.join(IMAGES_DIR, f"cd_{id_cd}.jpg")
        if os.path.exists(caratula_path):
            st.image(caratula_path, caption="Carátula actual", width=200)

        # 📌 Subir nueva carátula
        st.subheader("Subir Carátula del CD")
        imagen_subida = st.file_uploader("Elige una imagen", type=["jpg", "png", "jpeg"])

        if imagen_subida:
            nueva_ruta = guardar_caratula(id_cd, imagen_subida)
            if nueva_ruta:
                st.success("✅ Carátula guardada correctamente.")
                st.image(nueva_ruta, caption="Nueva carátula", width=200)

        # 📌 Estado de sesión para almacenar canciones temporalmente
        if "canciones_temporales" not in st.session_state:
            st.session_state.canciones_temporales = []

        # 📌 Formulario para agregar canciones a la lista temporal
        st.subheader("Añadir Canción Manualmente")

        disc_number = st.number_input("Número de CD", min_value=1, value=1)
        track_number = st.number_input("Número de Pista", min_value=1, value=1)
        interprete = st.text_input("Intérprete", "")
        titulo = st.text_input("Título de la Canción", "")
        url = st.text_input("URL de la Canción (opcional)", "")

        if st.button("Añadir a la lista"):
            if titulo and interprete:
                st.session_state.canciones_temporales.append({
                    "disc_number": disc_number,
                    "track_number": track_number,
                    "interprete": interprete,
                    "titulo": titulo,
                    "url": url
                })
                st.success(f"🎵 Canción '{titulo}' añadida a la lista temporal.")
            else:
                st.error("⚠️ El título y el intérprete son obligatorios.")

        # 📌 Mostrar lista de canciones antes de guardarlas
        if st.session_state.canciones_temporales:
            st.subheader("Lista de Canciones por Guardar:")
            for idx, cancion in enumerate(st.session_state.canciones_temporales):
                st.write(f"🎵 **{cancion['track_number']}. {cancion['titulo']}** - {cancion['interprete']}")
                if cancion['url']:
                    st.markdown(f"[🔗 Escuchar en Spotify]({cancion['url']})")

            # 📌 Botón para guardar todas las canciones en la base de datos
            if st.button("Guardar todas las canciones en la base de datos"):
                guardar_canciones(id_cd, st.session_state.canciones_temporales)
                st.success("✅ Todas las canciones han sido guardadas correctamente.")
                st.session_state.canciones_temporales = []  # Limpiar la lista después de guardar

        # 📌 Mostrar todas las canciones ya guardadas en la base de datos
        st.subheader("Canciones ya archivadas:")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT disc_number, track_number, interprete_cancion, cancion, cancion_url 
            FROM fonoteca_canciones WHERE id = ? ORDER BY disc_number, track_number;
        """, (id_cd,))
        canciones = cursor.fetchall()
        conn.close()

        if canciones:
            for cancion in canciones:
                st.write(f"🎵 **{cancion[1]}. {cancion[3]}** - {cancion[2]}")
                if cancion[4]:  # Si hay URL, mostrar enlace
                    st.markdown(f"[🔗 Escuchar en Spotify]({cancion[4]})")
        else:
            st.info("No hay canciones registradas aún.")