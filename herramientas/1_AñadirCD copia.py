import streamlit as st
import sqlite3
import os
import requests
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# 1_AñadirCD.py
# Añadir un nuevo Cd a la fonoteca
# Versión 2.0 05/02/2025 10:07
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.



#
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
st.sidebar.title("Añadir CD")
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
                <h1>Añadir CD</h1>
            </th>
        </tr>
    </table>
    ''',
    unsafe_allow_html=True,
)
#
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#
# 📌 Configuración de la base de datos
DB_PATH = "./db/FonotecaRadioUMH.db"

# 📌 Configuración de credenciales de Spotify
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"
AUTH_URL = "https://accounts.spotify.com/api/token"

# 📌 Función para obtener el token de autenticación de Spotify
def obtener_token_spotify():
    response = requests.post(AUTH_URL, {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })
    data = response.json()
    return data.get("access_token")

# 📌 Función para buscar un álbum en Spotify
def buscar_album_spotify(autor, titulo_cd, token):
    query = f"{titulo_cd} {autor}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=album&limit=1"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    if "albums" in data and data["albums"]["items"]:
        album = data["albums"]["items"][0]
        return album["id"], album["images"][0]["url"] if album["images"] else None
    return None, None

# 📌 Función para insertar un nuevo CD en la base de datos
def insertar_cd(numero_cd, autor, titulo_cd, id_cd_spotify, caratula_url):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO fonoteca_cd (numero_cd, autor, titulo_cd, id_cd, carátula_cd)
        VALUES (?, ?, ?, ?, ?);
    """, (numero_cd, autor, titulo_cd, id_cd_spotify, caratula_url))
    
    conn.commit()
    
    # 🔹 Obtener el ID del CD recién insertado
    cd_id = cursor.lastrowid
    
    conn.close()
    return cd_id  # Devolvemos el ID para usarlo en los siguientes pasos

# 📌 Interfaz de Streamlit
# st.sidebar.title("Alta de Nuevo CD")
st.markdown("<h2 style='color: #BD2830; text-align: center;'>Alta de Nuevo CD</h2>", unsafe_allow_html=True)

# 🔹 Formulario para dar de alta un nuevo CD
st.subheader("Introduce los datos del nuevo CD:")

numero_cd = st.text_input("Número de CD:")
autor = st.text_input("Autor:")
titulo_cd = st.text_input("Título del CD:")

# 🔹 Botón para registrar el CD y buscar en Spotify
if st.button("Buscar en SPOTIFY y Guardar en base de datos"):
    if numero_cd and autor and titulo_cd:
        # 🔹 Obtener el token de Spotify
        token = obtener_token_spotify()
        
        # 🔹 Buscar el álbum en Spotify
        id_cd_spotify, caratula_url = buscar_album_spotify(autor, titulo_cd, token)

        # 🔹 Guardar el CD en la base de datos con los datos obtenidos de Spotify
        cd_id = insertar_cd(numero_cd, autor, titulo_cd, id_cd_spotify, caratula_url)
        
        st.success(f"✅ CD '{titulo_cd}' de '{autor}' registrado correctamente.")

        # 🔹 Mostrar la carátula si se encontró
        if caratula_url:
            st.image(caratula_url, caption="Carátula obtenida de Spotify", width=200)
        else:
            st.warning("⚠️ No se encontró carátula en Spotify.")

        # 🔹 Sugerir siguiente paso
        st.info("Ahora debes añadir las canciones. Selecciona una de las siguientes opciones:")

        # 📌 Mostrar botones según si el CD tiene un `id_cd` de Spotify o no
        col1, col2 = st.columns(2)
        
        with col1:
            if id_cd_spotify:
                st.markdown("[🎵 Añadir Canciones desde Spotify](pages/9_AñadircancionesSpotify.py)")
            else:
                st.markdown("[🎵 Añadir Canciones Manualmente](pages/AgregarCancionesManualmente.py)")

    else:
        st.error("⚠️ Debes completar todos los campos obligatorios (Número de CD, Autor y Título).")