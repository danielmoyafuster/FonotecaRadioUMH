import pandas as pd
import streamlit as st
import os

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
    return pd.DataFrame(columns=["Nº", "AUTOR", "NOMBRE CD", "TITULO", "URL", "ID"])

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
        | datos["TITULO"].str.contains(query, case=False, na=False)
    ]

    if not resultados.empty:
        # Reemplazar NaN por "-"
        resultados = resultados.fillna("-")

        # Convertir las URLs en enlaces clicables
        resultados["URL"] = resultados["URL"].apply(
            lambda url: f'<a href="{url}" target="_blank">Escuchar ahora</a>' if url != "-" else "-"
        )

        # Eliminar la columna ID antes de mostrar la tabla
        resultados = resultados.drop(columns=["ID"], errors="ignore")

        # Mostrar los resultados en una tabla estilizada
        st.write("### Resultados de la búsqueda:")
        st.write(
            resultados[["Nº", "AUTOR", "NOMBRE CD", "TITULO", "URL"]].to_html(
                escape=False, index=False, classes="table table-striped", justify="left"
            ),
            unsafe_allow_html=True,
        )
    else:
        st.warning("⚠️ No se encontraron resultados para tu búsqueda.")
else:
    st.info("🔍 Ingresa un término en el campo de búsqueda para ver los resultados.")

# Mostrar todos los registros (opcional)
if st.checkbox("Mostrar todos los registros actuales"):
    st.write("### Registros actuales:")
    st.write(
        datos[["Nº", "AUTOR", "NOMBRE CD", "TITULO", "URL"]].fillna("-").to_html(
            escape=False, index=False, classes="table table-striped", justify="left"
        ),
        unsafe_allow_html=True,
    )