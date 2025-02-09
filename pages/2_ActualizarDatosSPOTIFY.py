import streamlit as st
import sqlite3
import requests
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# 2_ActualizarDatosSPOTIFY.py
# Actualizar Datos a CDs que no se encontraron automáticamente
# Versión 2.0 07/02/2025 11:50
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.


# -------------------------------------
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
st.sidebar.title("Actualizar datos desde SPOTIFY")
st.sidebar.caption("Versión 2.0 07/02/2025 11:50")
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



# 📌 Ruta de la base de datos SQLite
DB_PATH = "./db/FonotecaRadioUMH.db"

# 📌 Credenciales de Spotify
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"
AUTH_URL = "https://accounts.spotify.com/api/token"

def obtener_token_spotify():
    """ Obtiene el token de autenticación de Spotify """
    response = requests.post(AUTH_URL, {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })
    data = response.json()
    return data.get("access_token")

def obtener_info_spotify(id_cd_spotify, token):
    """ Obtiene la carátula y el género musical de un CD en Spotify """
    url = f"https://api.spotify.com/v1/albums/{id_cd_spotify}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    caratula_url = data["images"][0]["url"] if "images" in data and data["images"] else None
    generos = ", ".join(data.get("genres", [])) if "genres" in data else None

    return caratula_url, generos

def obtener_genero_artista(artist_name, token):
    """ Busca un artista en Spotify y obtiene su género musical si el álbum no lo tiene """
    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        artists = data.get("artists", {}).get("items", [])
        if artists:
            return ", ".join(artists[0].get("genres", []))
    return None

def obtener_cds_sin_canciones():
    """ Obtiene los CDs de la tabla `fonoteca_cd` que no tienen canciones en `fonoteca_canciones` """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fc.id, fc.titulo_cd, fc.autor 
        FROM fonoteca_cd fc
        LEFT JOIN fonoteca_canciones fca ON fc.id = fca.id
        WHERE fca.id IS NULL
        GROUP BY fc.id;
    """)
    cds = cursor.fetchall()
    conn.close()
    return cds

def actualizar_cd_en_bd(cd_id, nuevo_id_cd):
    """ Actualiza `id_cd`, `carátula_cd` y `genero_musical` en la base de datos """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 🔹 Obtener token de Spotify
        token = obtener_token_spotify()

        # 🔹 Obtener carátula y género musical desde Spotify
        caratula_url, genero_musical = obtener_info_spotify(nuevo_id_cd, token)

        # 🔹 Si no hay género en el álbum, buscar el del artista
        if not genero_musical:
            cursor.execute("SELECT autor FROM fonoteca_cd WHERE id = ?;", (cd_id,))
            autor = cursor.fetchone()[0]
            genero_musical = obtener_genero_artista(autor, token)

        # 🔹 Actualizar la base de datos
        cursor.execute("UPDATE fonoteca_cd SET id_cd = ?, carátula_cd = ?, genero_musical = ? WHERE id = ?;",
                       (nuevo_id_cd, caratula_url, genero_musical, cd_id))
        conn.commit()

    except sqlite3.Error as e:
        st.error(f"❌ Error al actualizar la base de datos: {e}")

    finally:
        conn.close()

    return caratula_url, genero_musical


# 🔹 Obtener la lista de CDs sin canciones
cds_sin_canciones = obtener_cds_sin_canciones()

if not cds_sin_canciones:
    st.success("✅ Todos los CDs tienen canciones. No hay nada que actualizar.")
else:
    opciones = {f"{id_cd} - {titulo} - {autor}": id_cd for id_cd, titulo, autor in cds_sin_canciones}
    seleccion = st.selectbox("Selecciona un CD sin canciones:", list(opciones.keys()))

    nuevo_id_cd = st.text_input("Introduce el `id_cd` de Spotify:")

    if st.button("Actualizar CD en la base de datos"):
        if nuevo_id_cd.strip():
            cd_id = opciones[seleccion]
            caratula_url, genero_musical = actualizar_cd_en_bd(cd_id, nuevo_id_cd)

            st.success(f"✅ `id_cd` actualizado correctamente para **{seleccion}**.")

            if caratula_url:
                st.image(caratula_url, caption="Carátula actualizada", width=200)
                st.success("📀 Carátula descargada y guardada correctamente.")
            else:
                st.warning("⚠️ No se encontró carátula para este CD en Spotify.")

            if genero_musical:
                st.success(f"🎵 Género musical obtenido: **{genero_musical}**")
            else:
                st.warning("⚠️ No se encontró género musical para este álbum o artista.")

            st.warning("📢 Ahora puedes ejecutar **Añadir Canciones Spotify** para sincronizar las canciones.")
        else:
            st.error("⚠️ Debes ingresar un `id_cd` antes de actualizar.")