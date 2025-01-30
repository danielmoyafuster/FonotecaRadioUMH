import pandas as pd
import streamlit as st
import os

#
# ACTUALIZACIÓN 30/01/25 06:00
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

# 📌 Ruta del archivo Excel
input_excel_path = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

# 📌 Función para cargar los datos existentes
def cargar_datos():
    if os.path.exists(input_excel_path):
        return pd.read_excel(input_excel_path)
    return pd.DataFrame(columns=["Nº", "AUTOR", "NOMBRE CD", "TITULO", "URL", "IMAGEN_URL", "ID"])

# 📌 Título de la página
st.title("🎵 Fonoteca de Radio UMH - Consulta")

# 📌 Cargar datos
datos = cargar_datos()

# 📌 Buscar registros
st.write("### 🔍 Buscar registros:")
query = st.text_input("🔎 Busca por Nº, AUTOR, NOMBRE CD o TÍTULO:")

if query:
    # 📌 Filtrar registros por la consulta
    resultados = datos[
        datos["Nº"].astype(str).str.contains(query, case=False, na=False)
        | datos["AUTOR"].str.contains(query, case=False, na=False)
        | datos["NOMBRE CD"].str.contains(query, case=False, na=False)
        | datos["TITULO"].str.contains(query, case=False, na=False)
    ]

    if not resultados.empty:
        # 📌 Reemplazar NaN por "-"
        resultados = resultados.fillna("-")

        # 📌 Eliminar duplicados basados en "Nº" y mantener solo la primera aparición
        resultados_unicos = resultados.drop_duplicates(subset=["Nº"], keep="first")

        # 📌 Crear opciones para el `selectbox` con un índice correcto
        opciones = resultados_unicos.apply(lambda row: f"{row['Nº']} - {row['AUTOR']} - {row['NOMBRE CD']}", axis=1).tolist()

        seleccion = st.selectbox("🎶 Selecciona un CD para ver detalles:", opciones)

        # 📌 Obtener datos del CD seleccionado
        num_seleccionado = seleccion.split(" - ")[0]  # Extraer el Nº del CD seleccionado
        fila_seleccionada = resultados_unicos[resultados_unicos["Nº"].astype(str) == num_seleccionado].iloc[0]

        # 📌 Mostrar carátula del CD (soporte para imágenes locales y URLs)
        imagen_url = fila_seleccionada["IMAGEN_URL"]
        if imagen_url and imagen_url != "-":
            if imagen_url.startswith("./imagenes_cd/"):  # 📌 Si es una imagen local
                if os.path.exists(imagen_url):  # 📌 Comprobar si el archivo existe
                    st.image(imagen_url, caption=fila_seleccionada["NOMBRE CD"], use_container_width=True)
                else:
                    st.warning(f"⚠️ La imagen local no se encontró en: {imagen_url}")
            else:
                st.image(imagen_url, caption=fila_seleccionada["NOMBRE CD"], use_container_width=True)
        else:
            st.warning("⚠️ Este CD no tiene carátula disponible.")

        # 📌 Mostrar las canciones del CD seleccionado con numeración corregida
        canciones = resultados[resultados["Nº"].astype(str) == num_seleccionado][["TITULO", "URL"]].drop_duplicates().reset_index(drop=True)

        if not canciones.empty:
            st.write("### 🎼 Canciones del CD:")
            for i, row in enumerate(canciones.itertuples(), start=1):  # 🔹 Enumeración desde 1
                titulo = row.TITULO
                url = row.URL if row.URL != "-" else None

                if url:
                    st.markdown(f"🎵 {i}. [{titulo}]({url})")  # 🔹 Enlace clickeable
                else:
                    st.write(f"🎵 {i}. {titulo}")  # 🔹 Canción sin URL

        else:
            st.warning("⚠️ No se encontraron canciones para este CD.")
    else:
        st.warning("⚠️ No se encontraron resultados para tu búsqueda.")
else:
    st.info("🔍 Ingresa un término en el campo de búsqueda para ver los resultados.")

# 📌 Mostrar todos los registros (opcional)
if st.checkbox("📜 Mostrar todos los registros actuales"):
    st.write("### 📋 Registros actuales:")
    
    # Seleccionar columnas relevantes
    columnas_a_mostrar = ["Nº", "AUTOR", "NOMBRE CD", "TITULO", "URL", "IMAGEN_URL"]
    datos_tabla = datos[columnas_a_mostrar].fillna("-")

    # Mostrar tabla en Streamlit sin formato HTML
    st.dataframe(datos_tabla, use_container_width=True)