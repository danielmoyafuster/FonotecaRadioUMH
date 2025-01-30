import pandas as pd
import streamlit as st
import os
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
#
# ACTUALIZACIÓN 30/01/25 09:00
#
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
CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Ruta del archivo Excel
input_excel_path = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

# 📌 Función para cargar datos desde Excel
@st.cache_data
def cargar_datos():
    if os.path.exists(input_excel_path):
        return pd.read_excel(input_excel_path)
    return pd.DataFrame(columns=["Nº", "AUTOR", "NOMBRE CD", "TITULO", "URL", "ID", "IMAGEN_URL"])

# 📌 Función para guardar datos en la Excel
def guardar_datos(df):
    df.to_excel(input_excel_path, index=False)

# 📌 Función para buscar canciones en Spotify
def buscar_canciones(autor, nombre_cd):
    resultados = sp.search(q=f"album:{nombre_cd} artist:{autor}", type="album", limit=1)
    if resultados["albums"]["items"]:
        album = resultados["albums"]["items"][0]
        album_id = album["id"]
        album_image_url = album["images"][0]["url"] if album["images"] else None  # URL de la imagen del álbum
        album_tracks = sp.album_tracks(album_id)
        canciones = [
            {
                "TITULO": track["name"],
                "URL": track["external_urls"]["spotify"],
                "ID": track["id"],
                "IMAGEN_URL": album_image_url  # Agregar la URL de la imagen
            }
            for track in album_tracks["items"]
        ]
        return canciones, album_image_url  # Devolver también la URL de la imagen
    return [], None

# 📌 Título de la aplicación
st.title("Fonoteca de Radio UMH - Añadir CD")

# 📌 Cargar datos existentes
datos = cargar_datos()

# 📌 Formulario para añadir un nuevo registro
with st.form("formulario_alta", clear_on_submit=True):
    nuevo_numero = st.text_input("Introduce el Nº (por ejemplo, 0001):")
    nuevo_autor = st.text_input("Introduce el AUTOR:")
    nuevo_nombre_cd = st.text_input("Introduce el NOMBRE CD:")

    # Botón para enviar el formulario
    submit = st.form_submit_button("Añadir registro y buscar canciones")

    if submit:
        st.write("Iniciando proceso de añadir registro...")
        st.write(f"Datos ingresados: Nº={nuevo_numero}, AUTOR={nuevo_autor}, NOMBRE CD={nuevo_nombre_cd}")

        if not (nuevo_numero and nuevo_autor and nuevo_nombre_cd):
            st.error("Por favor, completa todos los campos antes de añadir el registro.")
            st.stop()

        # 📌 Buscar canciones en Spotify
        canciones, album_image_url = buscar_canciones(nuevo_autor, nuevo_nombre_cd)
        st.write(f"Se encontraron {len(canciones)} canciones para el álbum '{nuevo_nombre_cd}' de '{nuevo_autor}'.")

        if not canciones:
            st.warning("⚠️ No se encontraron canciones para este álbum en Spotify.")
            
            # 🔹 Crear un registro indicando que no se encontró el álbum
            nuevo_registro = pd.DataFrame([{
                "Nº": nuevo_numero,
                "AUTOR": nuevo_autor,
                "NOMBRE CD": nuevo_nombre_cd,
                "TITULO": "Álbum no encontrado",
                "URL": None,
                "ID": None,
                "IMAGEN_URL": None
            }])

            # 🔹 Agregar este registro a la Excel
            datos = pd.concat([datos, nuevo_registro], ignore_index=True)
            
            # 🔹 Guardar cambios en la Excel
            try:
                guardar_datos(datos)
                st.success(f"⚠️ Álbum '{nuevo_nombre_cd}' de '{nuevo_autor}' no encontrado en Spotify. Se ha registrado en la base de datos.")
            except PermissionError:
                st.error("⚠️ No se puede guardar el archivo. Asegúrate de que no está abierto en otro programa.")
                st.stop()
            except Exception as e:
                st.error(f"Error al guardar los datos: {e}")
                st.stop()

            # 🔹 Detener ejecución tras guardar el registro
            st.stop()

        # 📌 Crear DataFrame con las canciones encontradas
        canciones_df = pd.DataFrame(canciones)
        canciones_df["Nº"] = nuevo_numero
        canciones_df["AUTOR"] = nuevo_autor
        canciones_df["NOMBRE CD"] = nuevo_nombre_cd

        # 📌 Concatenar al DataFrame existente
        datos = pd.concat([datos, canciones_df], ignore_index=True)

        # 📌 Guardar datos en Excel
        try:
            guardar_datos(datos)
            st.success(f"🎉 Se añadieron {len(canciones)} canciones del álbum '{nuevo_nombre_cd}' por '{nuevo_autor}'.")
        except PermissionError:
            st.error("⚠️ No se puede guardar el archivo. Asegúrate de que no está abierto en otro programa.")
            st.stop()
        except Exception as e:
            st.error(f"Error al guardar los datos: {e}")
            st.stop()

        # 📌 Recargar datos después de guardar
        datos = cargar_datos()
        st.write("✅ Datos recargados después de guardar.")

        # 📌 Mostrar la imagen del álbum debajo de la lista
        if album_image_url:
            st.image(album_image_url, caption=f"Carátula de '{nuevo_nombre_cd}' - {nuevo_autor}", use_container_width=True)
        else:
            st.warning("⚠️ No se encontró imagen para este álbum.")