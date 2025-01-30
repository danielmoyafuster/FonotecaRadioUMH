import pandas as pd
import requests
import base64
import streamlit as st
import os
import pyperclip  # 📋 Para copiar al portapapeles
#
# ACTUALIZACIÓN 30/01/25 06:00
#
st.sidebar.title("Corregir Álbum (SPOTIFY)")
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

# ----------------------------------------------------------------------------------------------------


# 📌 Función para copiar texto en Streamlit (sin pyperclip)
def copiar_al_portapapeles_streamlit(texto):
    st.text_input("📋 Copia este texto manualmente:", texto)



# 📌 Nombre del archivo Excel
EXCEL_FILE = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

# 📌 Función para obtener el token de autenticación de Spotify
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        st.error(f"⚠️ Error al obtener token: {response.text}")
        return None

# 📌 Cargar el archivo Excel
@st.cache_data
def load_excel():
    try:
        df = pd.read_excel(EXCEL_FILE)
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo Excel.")
        return pd.DataFrame()

df = load_excel()

# 📌 Filtrar álbumes no encontrados
df_no_encontrados = df[df["TITULO"] == "Álbum no encontrado"]

if not df_no_encontrados.empty:  
    st.title("Corrección de Álbumes No Encontrados - Spotify")

    # 📌 Crear opciones para el `selectbox` con el número de elementos
    opciones = df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1).tolist()
    num_elementos = len(opciones)  # 📌 Contar el número de álbumes en la lista

    # 📌 Mostrar el selectbox con la cantidad de álbumes disponibles
    seleccion = st.selectbox(f"Selecciona un álbum para buscar en Spotify ({num_elementos} disponibles):", opciones, key="album_selector")

    # 📌 Campo de texto para copiar manualmente el contenido del selectbox
    copiar_al_portapapeles_streamlit(seleccion)

    # 🔹 Resto del código para procesar la búsqueda en Spotify...