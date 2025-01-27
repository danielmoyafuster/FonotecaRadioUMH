import pandas as pd
import streamlit as st
import os
#
# ACTUALIZACIÓN 27/01/25 13:16
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

# Ruta del archivo Excel
input_excel_path = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

# Función para cargar los datos existentes
def cargar_datos():
    if os.path.exists(input_excel_path):
        return pd.read_excel(input_excel_path)
    return pd.DataFrame(columns=["Nº", "AUTOR", "NOMBRE CD", "TITULO", "URL", "IMAGEN_URL", "ID"])

# Título de la página
st.title("Fonoteca de Radio UMH - Consulta")

# Cargar datos
datos = cargar_datos()

# Buscar registros
st.write("### Buscar registros:")
query = st.text_input("🔍 Busca por Nº, AUTOR, NOMBRE CD o TÍTULO:")

if query:
    # Filtrar registros por la consulta
    resultados = datos[
        datos["Nº"].astype(str).str.contains(query, case=False, na=False)
        | datos["AUTOR"].str.contains(query, case=False, na=False)
        | datos["NOMBRE CD"].str.contains(query, case=False, na=False)
        | datos["TITULO"].str.contains(query, case=False, na=False)  # Agregado soporte para TÍTULO
    ]

    if not resultados.empty:
        # Reemplazar NaN por "-"
        resultados = resultados.fillna("-")

        # Eliminar duplicados basados en la columna "Nº"
        resultados_unicos = resultados.drop_duplicates(subset=["Nº"])

        # Crear opciones para el selectbox (Nº, AUTOR, NOMBRE CD)
        opciones = resultados_unicos[["Nº", "AUTOR", "NOMBRE CD"]].apply(
            lambda row: f"{row['Nº']} - {row['AUTOR']} - {row['NOMBRE CD']}", axis=1
        ).tolist()

        # Seleccionar un CD
        seleccion = st.selectbox("Selecciona un CD para ver detalles:", opciones)

        # Obtener datos del CD seleccionado
        fila_seleccionada = resultados_unicos.iloc[opciones.index(seleccion)]

        # Mostrar carátula del CD
        imagen_url = fila_seleccionada["IMAGEN_URL"]
        if imagen_url and imagen_url != "-":
            st.image(imagen_url, caption=fila_seleccionada["NOMBRE CD"], use_container_width=True)
        else:
            st.warning("⚠️ Este CD no tiene carátula disponible.")

        # Mostrar las canciones del CD seleccionado
        canciones = resultados[resultados["Nº"] == fila_seleccionada["Nº"]]["TITULO"].tolist()
        if canciones:
            st.write("### Canciones del CD:")
            for i, cancion in enumerate(canciones, start=1):
                st.write(f"{i}. {cancion}")
        else:
            st.warning("⚠️ No se encontraron canciones para este CD.")
    else:
        st.warning("⚠️ No se encontraron resultados para tu búsqueda.")
else:
    st.info("🔍 Ingresa un término en el campo de búsqueda para ver los resultados.")

# Mostrar todos los registros (opcional)
if st.checkbox("Mostrar todos los registros actuales"):
    st.write("### Registros actuales:")
    st.write(
        datos[["Nº", "AUTOR", "NOMBRE CD", "TITULO", "URL", "IMAGEN_URL"]].fillna("-").to_html(
            escape=False, index=False, classes="table table-striped", justify="left"
        ),
        unsafe_allow_html=True,
    )