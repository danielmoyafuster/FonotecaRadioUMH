import pandas as pd
import requests
import base64
import streamlit as st
import os
import pyperclip  # 📋 Para copiar al portapapeles
#
# ACTUALIZACIÓN 30/01/25 09:00
#
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



# 📌 Función para copiar texto al portapapeles (sin notificar al usuario)
def copiar_al_portapapeles(texto):
    pyperclip.copy(texto)

# 📌 Nombre del archivo Excel
EXCEL_FILE = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

# 📌 Función para cargar el archivo Excel
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
    st.title("🎵 Corrección de Álbumes No Encontrados - Manual")

    st.markdown("### 🎧 CD's no encontrados en SPOTIFY")
    
    opciones = df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1).tolist()
    
    col1, col2 = st.columns([4, 1])  

    with col1:
        seleccion = st.selectbox("Selecciona un álbum para modificar manualmente:", opciones, key="album_selector")

    with col2:
        if st.button("📋 Copiar al portapapeles"):
            copiar_al_portapapeles(seleccion)  # Copia sin notificación

    # 📌 Proceso de corrección manual
    if seleccion:
        # 🔹 Obtener el índice exacto de la fila seleccionada
        seleccion_index = df_no_encontrados[
            df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1) == seleccion
        ].index[0]

        autor_original = df.loc[seleccion_index, "AUTOR"]
        nombre_cd_original = df.loc[seleccion_index, "NOMBRE CD"]
        num_original = df.loc[seleccion_index, "Nº"]

        # 📌 Formulario para agregar canciones manualmente
        st.markdown("## 🎵 Añadir canciones manualmente")

        # 1️⃣ Campo para subir la imagen del CD
        uploaded_file = st.file_uploader("📀 Sube la imagen del CD (opcional)", type=["jpg", "png", "jpeg"])

        # 2️⃣ Campo para ingresar el título de la canción
        track_name = st.text_input("🎶 Título de la canción:")

        # 3️⃣ Botón para añadir la canción manualmente
        if st.button("➕ Añadir canción"):
            if track_name:
                new_track = {
                    "Nº": num_original,
                    "AUTOR": autor_original,  
                    "NOMBRE CD": nombre_cd_original,  
                    "TITULO": track_name,  
                    "URL": None,  
                    "ID": None,
                    "IMAGEN_URL": f"./imagenes_cd/{uploaded_file.name}" if uploaded_file else None  
                }
                if "track_list" not in st.session_state:
                    st.session_state.track_list = []
                st.session_state.track_list.append(new_track)
                st.rerun()  # 🔄 Recargar la interfaz para actualizar la lista

        # 📌 Mostrar lista de canciones añadidas en tiempo real
        if "track_list" in st.session_state and st.session_state.track_list:
            st.markdown("### 📋 Canciones añadidas manualmente:")
            for idx, track in enumerate(st.session_state.track_list, start=1):
                st.write(f"🎶 {idx}. {track['TITULO']}")

        # 📌 Botón para guardar las canciones manuales en la Excel
        if "track_list" in st.session_state and st.session_state.track_list and st.button("💾 Guardar canciones manuales"):
            df = pd.concat([df, pd.DataFrame(st.session_state.track_list)], ignore_index=True)

            # ✅ Eliminar el registro con "Álbum no encontrado"
            df = df.drop(index=seleccion_index).reset_index(drop=True)

            # ✅ Guardar en Excel
            df.to_excel(EXCEL_FILE, index=False)
            st.success("✅ Canciones manuales guardadas correctamente.")

            # 🔄 **Actualizar la lista del ComboBox de forma segura**
            df_no_encontrados = df[df["TITULO"] == "Álbum no encontrado"]
            opciones = df_no_encontrados.apply(lambda row: f"{row['AUTOR']} - {row['NOMBRE CD']}", axis=1).tolist()

            # **Eliminar la clave antes de modificar `session_state` para evitar errores**
            st.session_state.pop("album_selector", None)

            if opciones:
                # ✅ Actualizar el selectbox con los álbumes restantes
                st.session_state.album_selector = opciones[0]
            else:
                # ✅ Vaciar el selectbox si no hay más álbumes por corregir
                st.session_state.album_selector = None  

            # 🔄 Recargar la interfaz para actualizar la lista
            st.rerun()