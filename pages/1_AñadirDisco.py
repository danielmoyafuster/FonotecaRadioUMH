import pandas as pd
import streamlit as st
import os
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sqlite3
st.sidebar.title("Añadir Álbum")
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

# Configurar credenciales de Spotify
SPOTIFY_CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
SPOTIFY_CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                           client_secret=SPOTIFY_CLIENT_SECRET))

# Configurar título de la app
st.title("Dar de Alta un Nuevo CD en la Fonoteca 13:02")

# Ruta de la base de datos
db_path = "FonotecaRadioUMH.db"

# Formulario para ingresar los datos básicos del CD
st.subheader("Datos del Nuevo CD")
numero_cd = st.text_input("Número del CD:").strip()
autor_cd = st.text_input("Autor del CD:").strip()
nombre_cd = st.text_input("Nombre del CD:").strip()

# Inicializar `st.session_state` para almacenar datos y evitar que se pierdan al recargar
if "track_list" not in st.session_state:
    st.session_state.track_list = None

# Función para verificar si el CD ya existe en la base de datos
def cd_existe(numero):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM fonoteca WHERE numero = ?"
        cursor.execute(query, (numero,))
        resultado = cursor.fetchone()
    return resultado[0] > 0

# Botón para buscar en Spotify
if st.button("🔍 Buscar en Spotify"):
    if numero_cd and autor_cd and nombre_cd:
        # Verificar si el número de CD ya existe
        if cd_existe(numero_cd):
            st.error(f"⚠️ El número de CD **{numero_cd}** ya está registrado en la fonoteca.")
        else:
            # Buscar el álbum en Spotify
            query = f"{nombre_cd} {autor_cd}"
            result = sp.search(q=query, type="album", limit=1)

            if result["albums"]["items"]:
                album_data = result["albums"]["items"][0]
                spotify_album_id = album_data["id"]
                spotify_album_url = album_data["external_urls"]["spotify"]
                album_cover = album_data["images"][0]["url"] if album_data["images"] else "No disponible"

                # Obtener lista de canciones del álbum
                track_list = []
                album_tracks = sp.album_tracks(spotify_album_id)

                for track in album_tracks["items"]:
                    track_list.append({
                        "numero": numero_cd,
                        "autor": ", ".join([artist["name"] for artist in track["artists"]]),
                        "nombre_cd": nombre_cd,
                        "titulo": f'<a href="{track["external_urls"]["spotify"]}" target="_blank">{track["name"]}</a>',  # 🔗 Enlace en el título
                        "url": track["external_urls"]["spotify"],  # No se mostrará en la tabla
                        "spotify_id": track["id"],  # No se mostrará en la tabla
                        "imagen_url": album_cover  # No se mostrará en la tabla
                    })

                # Guardar la lista en `st.session_state`
                st.session_state.track_list = pd.DataFrame(track_list)

                # 📌 Mostrar los datos antes de guardar con enlaces activos y sin columnas innecesarias
                st.subheader("🎵 Canciones encontradas")
                st.write(f"✅ Álbum encontrado en Spotify: **[{nombre_cd}]({spotify_album_url})**")
                st.image(album_cover, caption="Carátula del CD", width=300)
                
                # Mostrar la tabla con títulos enlazados y sin columnas innecesarias
                columnas_a_mostrar = ["numero", "autor", "nombre_cd", "titulo"]
                st.write(st.session_state.track_list[columnas_a_mostrar].to_html(escape=False, index=False), unsafe_allow_html=True)

# 📌 Botón de guardar solo si hay canciones en `st.session_state`
if st.session_state.track_list is not None:
    if st.button("💾 Guardar CD en la Fonoteca"):
        st.write("📊 **Guardando datos en la base de datos...**")

        # 📌 Guardar los datos en la base de datos
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Insertar datos manualmente
                for _, row in st.session_state.track_list.iterrows():
                    cursor.execute("""
                        INSERT INTO fonoteca (numero, autor, nombre_cd, titulo, url, spotify_id, imagen_url) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (row["numero"], row["autor"], row["nombre_cd"], row["titulo"], row["url"], row["spotify_id"], row["imagen_url"]))
                
                conn.commit()

                # 🔍 Verificar si los datos realmente se han guardado
                query_verificacion = "SELECT * FROM fonoteca WHERE numero = ?"
                verificacion_df = pd.read_sql_query(query_verificacion, conn, params=(numero_cd,))
                
                st.write("🔎 **Verificación en la base de datos después de guardar:**")
                if verificacion_df.empty:
                    st.error("❌ Los datos NO se han guardado en la base de datos. Algo está fallando.")
                else:
                    st.success(f"✅ El álbum '{nombre_cd}' de {autor_cd} ha sido agregado a la fonoteca.")
                    st.dataframe(verificacion_df)

                # ✅ Limpiar `st.session_state` después de guardar
                st.session_state.track_list = None

        except Exception as e:
            st.error(f"❌ Error al guardar en la base de datos: {e}")