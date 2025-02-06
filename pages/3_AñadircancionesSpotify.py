import streamlit as st
import sqlite3
import requests
import time

# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# 3_AñadircancionesSpotify.py
# Añadir Canciones al CD desde SPOTIFY
# Versión 2.0 05/02/2025 10:07
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.


#
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
st.sidebar.title("Buscar canciones en SPOTIFY")
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


# 📌 Configurar credenciales de Spotify
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

# 📌 Ruta de la base de datos SQLite
DB_PATH = "./db/FonotecaRadioUMH.db"

# 📌 URL de autenticación de Spotify
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

def obtener_canciones_album(id_cd_spotify, token):
    """ Obtiene todas las canciones de un álbum en Spotify """
    url = f"https://api.spotify.com/v1/albums/{id_cd_spotify}/tracks?limit=50"
    headers = {"Authorization": f"Bearer {token}"}

    canciones = []
    
    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        for track in data.get("items", []):
            canciones.append({
                "disc_number": track["disc_number"],  
                "track_number": track["track_number"],  
                "interprete": track["artists"][0]["name"],  
                "cancion": track["name"],  
                "cancion_url": track["external_urls"]["spotify"] if "external_urls" in track else None
            })

        url = data.get("next")  # 🔹 Si hay más páginas, seguimos obteniendo más canciones
    
    return canciones

def obtener_cds_pendientes():
    """ Obtiene el número de CDs que aún no tienen canciones en la base de datos """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) 
        FROM fonoteca_cd fc
        LEFT JOIN fonoteca_canciones fca ON fc.id = fca.id
        WHERE fc.id_cd IS NOT NULL AND fc.id_cd != '' 
        GROUP BY fc.id 
        HAVING COUNT(fca.id) = 0;
    """)
    
    cds_pendientes = len(cursor.fetchall())
    conn.close()
    
    return cds_pendientes

def importar_canciones():
    """ Importa las canciones desde Spotify para los CDs pendientes """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fc.id, fc.id_cd 
        FROM fonoteca_cd fc
        LEFT JOIN fonoteca_canciones fca ON fc.id = fca.id
        WHERE fc.id_cd IS NOT NULL AND fc.id_cd != '' 
        GROUP BY fc.id 
        HAVING COUNT(fca.id) = 0;
    """)
    cds = cursor.fetchall()
    conn.close()

    if not cds:
        st.success("✅ Todos los CDs ya tienen canciones archivadas. No hay nada que importar.")
        return

    token = obtener_token_spotify()
    progress_bar = st.progress(0)
    total_cds = len(cds)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        for index, (id_cd_local, id_cd_spotify) in enumerate(cds):
            canciones = obtener_canciones_album(id_cd_spotify, token)

            for cancion in canciones:
                cursor.execute("""
                    INSERT INTO fonoteca_canciones (id, disc_number, interprete_cancion, track_number, cancion, cancion_url)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (id_cd_local, cancion["disc_number"], cancion["interprete"], cancion["track_number"], cancion["cancion"], cancion["cancion_url"]))

            conn.commit()
            progress_bar.progress((index + 1) / total_cds)
            time.sleep(0.5)

        st.success("✅ Proceso finalizado: Todas las canciones han sido archivadas correctamente.")

    except Exception as e:
        st.error(f"❌ Error durante la importación: {e}")

    finally:
        conn.close()

# 📌 Interfaz en Streamlit
st.markdown("<h2 style='color: #BD2830; text-align: center;'>Actualizar Canciones desde Spotify</h2>", unsafe_allow_html=True)
st.write("Este módulo buscará los CDs en la base de datos que aún no tienen canciones importadas desde Spotify y procederá a archivarlas.")

# 📌 Mostrar el número de CDs pendientes antes del botón
cds_pendientes = obtener_cds_pendientes()
st.markdown(f"### 🎵 CD's pendientes de actualizar: **{cds_pendientes}**")

if st.button("Iniciar Importación"):
    importar_canciones()