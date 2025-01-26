import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
import os

# Configurar credenciales de Spotify
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Ruta del archivo Excel
input_excel_path = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

# Función para cargar los datos existentes
@st.cache_data
def cargar_datos():
    if os.path.exists(input_excel_path):
        return pd.read_excel(input_excel_path)
    return pd.DataFrame(columns=["Nº", "AUTOR", "NOMBRE CD", "TITULO", "URL", "ID"])

# Guardar datos en el archivo Excel
def guardar_datos(df):
    df.to_excel(input_excel_path, index=False)

# Función para buscar canciones en Spotify
def buscar_canciones(autor, nombre_cd):
    resultados = sp.search(q=f"album:{nombre_cd} artist:{autor}", type="album", limit=1)
    if resultados["albums"]["items"]:
        album_id = resultados["albums"]["items"][0]["id"]
        album_tracks = sp.album_tracks(album_id)
        canciones = [
            {
                "TITULO": track["name"],
                "URL": track["external_urls"]["spotify"],
                "ID": track["id"],
            }
            for track in album_tracks["items"]
        ]
        return canciones
    return []

# Inicializar estado
if "data" not in st.session_state:
    st.session_state.data = cargar_datos()

# Mostrar el logo de Radio UMH con enlace
st.markdown(
    """
    <div style="text-align: center;">
        <a href="https://radio.umh.es/presentacion/" target="_blank">
            <img src="https://radio.umh.es/files/2023/07/FOTO-PERFIL-RADIO.png" alt="Radio UMH" style="width: 200px; margin-bottom: 20px;">
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# Cambiado el literal del título
st.title("Gestión de la Fonoteca de Radio UMH")

# Buscar registros
st.write("### Buscar registros:")
query = st.text_input("🔍 Busca por AUTOR, NOMBRE CD o TÍTULO:")

if query:
    resultados = st.session_state.data[
        st.session_state.data["AUTOR"].str.contains(query, case=False, na=False)
        | st.session_state.data["NOMBRE CD"].str.contains(query, case=False, na=False)
        | st.session_state.data["TITULO"].str.contains(query, case=False, na=False)
    ]

    if not resultados.empty:
        # Reemplazar NaN por "-"
        resultados = resultados.fillna("-")

        # Convertir la URL en un enlace dinámico con texto "Escuchar ahora"
        resultados["URL"] = resultados["URL"].apply(
            lambda url: f'<a href="{url}" target="_blank">Escuchar ahora</a>' if url != "-" else "-"
        )

        # Eliminar la columna ID para mostrar en la tabla
        resultados = resultados.drop(columns=["ID"])

        # Mostrar resultados con estilo alineado a la izquierda
        st.write("### Resultados de la búsqueda:")
        st.write(
            resultados.to_html(escape=False, index=False, classes="table table-striped", justify="left"),
            unsafe_allow_html=True,
        )
    else:
        st.warning("⚠️ No se encontraron resultados.")
else:
    st.info("🔍 Ingresa un término en el campo de búsqueda para ver resultados.")

# Añadir un nuevo registro
st.write("### Añadir un nuevo registro:")

# Crear formulario para manejar los inputs
with st.form("formulario_registro", clear_on_submit=True):
    nuevo_numero = st.text_input("Introduce el Nº (por ejemplo, 0001):")
    nuevo_autor = st.text_input("Introduce el AUTOR:")
    nuevo_nombre_cd = st.text_input("Introduce el NOMBRE CD:")

    # Botón para enviar el formulario
    submit = st.form_submit_button("Añadir registro y buscar canciones")

    if submit:
        if nuevo_numero and nuevo_autor and nuevo_nombre_cd:
            # Buscar canciones en Spotify
            canciones = buscar_canciones(nuevo_autor, nuevo_nombre_cd)

            if canciones:
                # Crear un DataFrame para las canciones encontradas
                canciones_df = pd.DataFrame(canciones)
                canciones_df["Nº"] = nuevo_numero
                canciones_df["AUTOR"] = nuevo_autor
                canciones_df["NOMBRE CD"] = nuevo_nombre_cd

                # Concatenar el nuevo registro
                st.session_state.data = pd.concat(
                    [st.session_state.data, canciones_df], ignore_index=True
                )

                # Guardar datos
                guardar_datos(st.session_state.data)

                # Mostrar mensaje de éxito
                st.success(f"🎉 Se añadieron {len(canciones)} canciones del álbum '{nuevo_nombre_cd}' por '{nuevo_autor}'.")
            else:
                st.warning("⚠️ No se encontraron canciones para este álbum en Spotify.")
        else:
            st.error("Por favor, completa todos los campos antes de añadir el registro.")
# Enlace a la página Eliminar Registros
st.markdown(
    """
    <div style="text-align: center; margin-top: 20px;">
        <a href="/?page=1_EliminarRegistros.py" target="_self" style="text-decoration: none; font-size: 18px; color: #007BFF;">
            ➡️ Eliminar Registros
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)