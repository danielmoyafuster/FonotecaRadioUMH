import pandas as pd
import requests
import base64
import streamlit as st
import pyperclip  # Para copiar al portapapeles
import os

#
# ACTUALIZACIÓN 30/01/25 06:00
#

# 📌 Función para copiar al portapapeles
def copiar_al_portapapeles(texto):
    pyperclip.copy(texto)

# 📌 Nombre del archivo Excel
EXCEL_FILE = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

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
df_no_encontrados = df[df["TITULO"].isin(["Álbum no encontrado", "Usando datos anteriores"])]

if not df_no_encontrados.empty:  
    st.title("🎵 Corrección de Álbumes No Encontrados")
    
    st.markdown("### 🎧 CD's no encontrados en SPOTIFY")
    
    opciones = df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1).tolist()
    
    col1, col2 = st.columns([4, 1])  
    
    with col1:
        seleccion = st.selectbox("Selecciona un álbum para corregir:", opciones, key="album_selector")

    with col2:
        if st.button("📋 Copiar al portapapeles"):
            copiar_al_portapapeles(seleccion)

    if seleccion:
        seleccion_index = df_no_encontrados[df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1) == seleccion].index[0]
        autor_original = df.loc[seleccion_index, "AUTOR"]
        nombre_cd_original = df.loc[seleccion_index, "NOMBRE CD"]
        num_original = df.loc[seleccion_index, "Nº"]

        # 🔹 Inicializar lista de canciones en el estado de sesión solo si no está ya creada
        if "track_list" not in st.session_state:
            st.session_state.track_list = []

        st.markdown("## 🎵 Añadir canciones manualmente")

        # 1️⃣ Nombre de la imagen del CD (en ./imagenes_cd)
        image_name = st.text_input("📀 Nombre del archivo de la imagen (Ej: portada.jpg):", key="image_input")

        # 2️⃣ Título de la canción
        track_name = st.text_input("🎵 Título de la canción:", key="track_input")

        # 3️⃣ Botón para añadir la canción manualmente (Evita registros vacíos)
        if st.button("➕ Añadir canción manual"):
            if track_name.strip():  # 📌 Verifica que no esté vacío
                # 📌 Verificar si la imagen existe antes de guardarla
                image_path = f"./imagenes_cd/{image_name}" if image_name else None
                if image_path and not os.path.exists(image_path):
                    st.warning(f"⚠️ La imagen '{image_name}' no existe en ./imagenes_cd/")
                    image_path = None  # No guardar la ruta si la imagen no existe

                new_track = {
                    "Nº": num_original,
                    "AUTOR": autor_original,  
                    "NOMBRE CD": nombre_cd_original,  
                    "TITULO": track_name.strip(),  
                    "URL": None,  
                    "ID": None,
                    "IMAGEN_URL": image_path  
                }
                st.session_state.track_list.append(new_track)
                st.rerun()  # 🔄 Recargar la interfaz para actualizar la lista
            else:
                st.warning("⚠️ No puedes agregar una canción sin título.")

        # 🔹 Mostrar la lista de canciones añadidas en tiempo real con un diseño más claro
        if st.session_state.track_list:
            st.markdown("### 📋 Canciones añadidas manualmente:")
            for idx, track in enumerate(st.session_state.track_list, start=1):
                st.write(f"🎶 **{idx}.** {track['TITULO']}")

        # 🔹 Botón para guardar todas las canciones en la Excel
        if st.session_state.track_list:
            if st.button("💾 Guardar canciones manuales"):
                # 📌 Filtrar registros incorrectos antes de guardar
                canciones_validas = [track for track in st.session_state.track_list]

                if canciones_validas:
                    df = pd.concat([df, pd.DataFrame(canciones_validas)], ignore_index=True)

                    # ✅ Eliminar todas las filas con "Álbum no encontrado" o "Usando datos anteriores"
                    df = df[~df["TITULO"].isin(["Álbum no encontrado", "Usando datos anteriores"])].reset_index(drop=True)

                    df.to_excel(EXCEL_FILE, index=False)
                    st.success("✅ Canciones manuales guardadas correctamente y álbum corregido.")

                    # 🔄 Limpiar la lista después de guardar y actualizar la interfaz
                    st.session_state.track_list = []
                    st.rerun()
                else:
                    st.warning("⚠️ No hay canciones válidas para guardar.")