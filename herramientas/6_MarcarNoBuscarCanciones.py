import streamlit as st
import sqlite3
import pandas as pd


# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# 6_MarcarNoBuscarCanciones.py
# Canciones que no encontramos por ningún sitio. Marcamos como
# no buscar más
# Versión 2.0 07/02/2025 12:47
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.



#
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
st.sidebar.title("Marcar No Buscar")
st.sidebar.caption("Versión 2.0 07/02/2025 12:47")
st.markdown(
    '''
    <style>
        /* 🔹 Quitar bordes de la tabla */
        table {
            border-collapse: collapse;
            border: none;
            background: transparent;
            width: 100%;
        }

        /* 🔹 Quitar bordes y fondo de las celdas */
        th, td {
            border: none !important;
            background: transparent !important;
            padding: 10px;
        }

        /* 🔹 Ajustar tamaño y estilos de la imagen */
        .logo-container img {
            width: 180px;  /* Aumentamos un poco el tamaño */
            border-radius: 10px;
            transition: transform 0.2s;
        }

        /* 🔹 Efecto hover en la imagen */
        .logo-container img:hover {
            transform: scale(1.1); /* Hace que la imagen se agrande un poco al pasar el ratón */
        }

        /* 🔹 Centrar el título */
        .title-container h1 {
            color: #BD2830;
            text-align: center;
            font-size: 30px;
        }
    </style>

    <table>
        <tr>
            <th class="logo-container">
                <a href="https://radio.umh.es/" target="_blank">
                    <img src="https://radio.umh.es/files/2023/07/FOTO-PERFIL-RADIO.png" 
                         alt="Radio UMH">
                </a>
            </th>
            <th class="title-container">
                <h1>Consultar la Fonoteca</h1>
            </th>
        </tr>
    </table>
    ''',
    unsafe_allow_html=True,
)
#
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#

#
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#
import streamlit as st
import sqlite3
import pandas as pd

# 📌 Ruta de la base de datos SQLite
DB_PATH = "./db/FonotecaRadioUMH.db"

# 📌 Función para obtener canciones sin URL en Spotify
def obtener_canciones_sin_url():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, disc_number, track_number, interprete_cancion, cancion, no_buscar 
        FROM fonoteca_canciones 
        WHERE (cancion_url IS NULL OR cancion_url = '') 
        AND no_buscar = 0
        ORDER BY id, disc_number, track_number;
    """)
    canciones = cursor.fetchall()
    conn.close()
    return canciones

# 📌 Función para actualizar la base de datos y marcar canciones como "No buscar"
def marcar_no_buscar(canciones):
    if canciones:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        cursor.executemany(
            "UPDATE fonoteca_canciones SET no_buscar = 1 WHERE id = ? AND disc_number = ? AND track_number = ?;",
            [(c[0], c[1], c[2]) for c in canciones]
        )
        conn.commit()
        conn.close()
        return True
    return False

# 📌 Interfaz de Streamlit
st.markdown("<h2 style='color: #BD2830; text-align: center;'>Marcar Canciones para No Buscar</h2>", unsafe_allow_html=True)
st.write("Aquí puedes ver las canciones sin enlace en Spotify y marcar las que no quieres que se busquen nuevamente.")

# 🔹 Obtener canciones sin URL
canciones_sin_url = obtener_canciones_sin_url()

if not canciones_sin_url:
    st.success("✅ No hay canciones pendientes de búsqueda en Spotify.")
else:
    # 🔹 Crear un DataFrame
    df = pd.DataFrame(canciones_sin_url, columns=["ID", "Disc Number", "Track Number", "Intérprete", "Canción", "No Buscar"])

    # 📌 Manejo de `st.session_state`
    if "checkbox_states" not in st.session_state:
        st.session_state.checkbox_states = {}

    # 🔹 Crear checkboxes con claves únicas usando el índice del DataFrame
    seleccionados = []
    for index, row in df.iterrows():
        unique_key = f"{row['ID']}_{row['Disc Number']}_{row['Track Number']}_{index}"  # 🔹 Agregamos `index` para hacer la clave única

        # Inicializar el estado del checkbox si no está en `session_state`
        if unique_key not in st.session_state.checkbox_states:
            st.session_state.checkbox_states[unique_key] = False

        # Checkbox con el estado almacenado en `session_state`
        marcado = st.checkbox(f"{row['Intérprete']} - {row['Canción']}", key=unique_key, value=st.session_state.checkbox_states[unique_key])

        # Guardar el estado
        st.session_state.checkbox_states[unique_key] = marcado

        if marcado:
            seleccionados.append((row["ID"], row["Disc Number"], row["Track Number"]))

    # 🔹 Botón para seleccionar todas las canciones
    if st.button("Seleccionar Todas"):
        for key in st.session_state.checkbox_states:
            st.session_state.checkbox_states[key] = True
        st.rerun()  # Recargar la página para aplicar los cambios

    # 🔹 Botón para desmarcar todas las canciones
    if st.button("Desmarcar Todas"):
        for key in st.session_state.checkbox_states:
            st.session_state.checkbox_states[key] = False
        st.rerun()  # Recargar la página para aplicar los cambios

    # 🔹 Botón para aplicar cambios en la base de datos
    if st.button("Actualizar 'No Buscar' en la Base de Datos"):
        if marcar_no_buscar(seleccionados):
            st.success(f"✅ Se han marcado {len(seleccionados)} canciones como 'No buscar'.")
            st.rerun()  # 🔹 Recargar la página para actualizar los cambios
        else:
            st.warning("⚠️ No se ha seleccionado ninguna canción.")