import streamlit as st
import shutil
import os

# 📌 Rutas de la base de datos
DB_REMOTA = "./db/FonotecaRadioUMH.db"  # Ruta en el repositorio remoto
DB_LOCAL = "/Users/danielmoyafuster/canciones/FonotecaRadioUMH/db/FonotecaRadioUMH.db"  # Ruta en el repositorio local

# 📌 Función para copiar la base de datos
def copiar_base_de_datos():
    try:
        # Verificar si la base de datos remota existe
        if not os.path.exists(DB_REMOTA):
            return "❌ No se encontró la base de datos en el repositorio remoto."

        # Copiar la base de datos al repositorio local
        shutil.copy(DB_REMOTA, DB_LOCAL)

        return "✅ Base de datos copiada correctamente del repositorio remoto al local."

    except Exception as e:
        return f"❌ Error al copiar la base de datos: {e}"

# 📌 Interfaz en Streamlit
st.sidebar.title("Copiar Base de Datos")

st.markdown("<h2 style='color: #BD2830; text-align: center;'>Copiar Base de Datos</h2>", unsafe_allow_html=True)
st.write("Este módulo copia la base de datos desde el **repositorio remoto** al **repositorio local**.")

if st.button("Copiar Base de Datos"):
    resultado = copiar_base_de_datos()
    st.write(resultado)