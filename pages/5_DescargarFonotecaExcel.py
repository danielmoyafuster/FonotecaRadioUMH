import streamlit as st

#
# ACTUALIZACIÓN 30/01/25 06:00
#
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


# Título de la aplicación
st.title("Descarga de Excel: FONOTECA_CD_UMH_SPOTIFY")

# Ruta del archivo Excel que se quiere ofrecer para descarga
excel_file_path = "FONOTECA_CD_UMH_SPOTIFY.xlsx"

# Verificar si el archivo existe
try:
    with open(excel_file_path, "rb") as file:
        # Leer el contenido del archivo
        excel_data = file.read()
    
    # Mostrar un botón para descargar el archivo
    st.download_button(
        label="📥 Descargar Excel",
        data=excel_data,
        file_name="FONOTECA_CD_UMH_SPOTIFY.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
except FileNotFoundError:
    st.error(f"El archivo {excel_file_path} no se encontró. Asegúrate de que el archivo existe en la ruta especificada.")