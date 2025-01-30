import pandas as pd
import streamlit as st
import os

#
# ACTUALIZACIÓN 30/01/25 09:00
#

# Encabezado en el menú lateral
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

# Función para cargar datos (sin caché)
def cargar_datos():
    if os.path.exists(input_excel_path):
        return pd.read_excel(input_excel_path)
    return pd.DataFrame(columns=["Nº", "AUTOR", "NOMBRE CD", "TITULO", "URL", "ID"])

# Función para guardar datos en el archivo Excel
def guardar_datos(df):
    df.to_excel(input_excel_path, index=False)

# Cargar datos
st.title("Fonoteca de Radio UMH - Borrar CD")
datos = cargar_datos()

# Limpieza de datos
datos["Nº"] = datos["Nº"].astype(str).str.strip()

# Búsqueda por Nº
st.write("### Buscar registros por Nº:")
numero_cd = st.text_input("Introduce el Nº del CD para buscar (por ejemplo, 0001):")

if numero_cd:
    # Limpiar el valor ingresado
    numero_cd = numero_cd.strip()

    # Filtrar registros
    registros_filtrados = datos[datos["Nº"] == numero_cd]

    if not registros_filtrados.empty:
        # Mostrar registros filtrados
        st.write("### Registros encontrados:")
        st.write(
            registros_filtrados[["Nº", "AUTOR", "NOMBRE CD", "TITULO"]].to_html(
                escape=False, index=False, classes="table table-striped", justify="left"
            ),
            unsafe_allow_html=True,
        )

        # Confirmar eliminación
        if st.button("Eliminar registros"):
            # Eliminar registros de los datos
            datos = datos[datos["Nº"] != numero_cd]

            # Guardar los cambios en el archivo Excel
            try:
                guardar_datos(datos)
                st.success(f"Los registros con Nº '{numero_cd}' se han eliminado correctamente.")
            except Exception as e:
                st.error(f"Error al guardar los cambios: {e}")

            # Recargar los datos actualizados
            datos = cargar_datos()
    else:
        st.warning(f"No se encontraron registros con el Nº '{numero_cd}'.")
else:
    st.info("Introduce un Nº para buscar registros.")

# Mostrar todos los registros (opcional)
if st.checkbox("Mostrar todos los registros actuales"):
    st.write("### Registros actuales:")
    st.write(
        datos[["Nº", "AUTOR", "NOMBRE CD", "TITULO"]].to_html(index=False, classes="table table-striped"),
        unsafe_allow_html=True,
    )