import streamlit as st
import sqlite3
import requests
#
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
st.sidebar.title("Actualizar datos desde SPOTIFY")
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
import requests

# 📌 Configuración de la base de datos SQLite
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

def obtener_caratula_spotify(id_cd_spotify, token):
    """ Obtiene la URL de la carátula de un CD en Spotify """
    url = f"https://api.spotify.com/v1/albums/{id_cd_spotify}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    if "images" in data and data["images"]:
        return data["images"][0]["url"]
    else:
        return None  # Si no hay imagen, devuelve None

def obtener_cds_sin_id_cd():
    """ Obtiene los CDs que no tienen un id_cd en Spotify """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo_cd, autor FROM fonoteca_cd WHERE id_cd IS NULL OR id_cd = '';")
    cds = cursor.fetchall()
    conn.close()
    return cds

def actualizar_id_cd_y_caratula(cd_id, nuevo_id_cd):
    """ Actualiza el id_cd y la carátula en la base de datos """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 🔹 Actualizar id_cd
        cursor.execute("UPDATE fonoteca_cd SET id_cd = ? WHERE id = ?;", (nuevo_id_cd, cd_id))
        conn.commit()

        # 🔹 Obtener token de Spotify
        token = obtener_token_spotify()

        # 🔹 Obtener la carátula del CD desde Spotify
        caratula_url = obtener_caratula_spotify(nuevo_id_cd, token)

        if caratula_url:
            cursor.execute("UPDATE fonoteca_cd SET carátula_cd = ? WHERE id = ?;", (caratula_url, cd_id))
            conn.commit()
            st.write(f"📀 Carátula guardada en la base de datos: {caratula_url}")  # 🔹 Debugging

        # 🔹 Verificación de que se guardó correctamente
        cursor.execute("SELECT id_cd, carátula_cd FROM fonoteca_cd WHERE id = ?;", (cd_id,))
        resultado = cursor.fetchone()
        st.write(f"✅ Verificación en base de datos: ID_CD={resultado[0]}, Carátula={resultado[1]}")

    except sqlite3.Error as e:
        st.error(f"❌ Error al actualizar la base de datos: {e}")

    finally:
        conn.close()

    return caratula_url


# 🔹 Obtener la lista de CDs sin id_cd
cds_sin_id = obtener_cds_sin_id_cd()

if not cds_sin_id:
    st.success("✅ Todos los CDs tienen un `id_cd`. No hay nada que actualizar.")
else:
    opciones = {f"{titulo} - {autor}": id for id, titulo, autor in cds_sin_id}
    seleccion = st.selectbox("Selecciona un CD sin `id_cd`:", list(opciones.keys()))

    nuevo_id_cd = st.text_input("Introduce el `id_cd` de Spotify:")

    if st.button("Actualizar CD en la base de datos"):
        if nuevo_id_cd.strip():
            cd_id = opciones[seleccion]
            caratula_url = actualizar_id_cd_y_caratula(cd_id, nuevo_id_cd)
            st.success(f"✅ `id_cd` actualizado correctamente para **{seleccion}**.")

            if caratula_url:
                st.image(caratula_url, caption="Carátula actualizada", width=200)
                st.success("📀 Carátula descargada y guardada correctamente.")
            else:
                st.warning("⚠️ No se encontró carátula para este CD en Spotify.")

            st.warning("📢 Ahora puedes ejecutar ** Añadir Canciones Spotify**  para sincronizar las canciones.")
        else:
            st.error("⚠️ Debes ingresar un `id_cd` antes de actualizar.")