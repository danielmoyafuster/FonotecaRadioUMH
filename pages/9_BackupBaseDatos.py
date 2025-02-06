import streamlit as st
import sqlite3
import shutil
import time
import os
from datetime import datetime
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# 9_BackupBaseDatos.py
# Backup de la base de datos
# Versión 2.0 05/02/2025 10:07
# .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

#
# configurar la estetica de la página
#
# 📌 Configurar la barra lateral
st.sidebar.title("Backup de la base de datos")
st.sidebar.caption("Versión 2.0 05/02/2025 10:07")
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

import streamlit as st
import sqlite3
import shutil
import time
import os
import re
import pandas as pd
from datetime import datetime

# 📌 Rutas
DB_PATH = "./db/FonotecaRadioUMH.db"
BACKUP_DIR = "./backups"
os.makedirs(BACKUP_DIR, exist_ok=True)  # Crear carpeta si no existe

# 📌 Patrón para extraer fecha y hora de los archivos de backup
BACKUP_PATTERN = re.compile(r"FonotecaRadioUMH_backup_(\d{8})_(\d{4})\.db")

# 📌 Función para obtener los backups existentes
def obtener_archivos_backup():
    """ Devuelve una lista de archivos de backup ordenados por fecha y hora (más recientes primero). """
    archivos = []
    for archivo in os.listdir(BACKUP_DIR):
        match = BACKUP_PATTERN.match(archivo)
        if match:
            fecha_str = match.group(1)  # AAAAMMDD
            hora_str = match.group(2)  # HHMM
            fecha_hora = datetime.strptime(fecha_str + hora_str, "%Y%m%d%H%M")  # Convertir a objeto datetime
            archivos.append((fecha_hora, archivo))

    return sorted(archivos, reverse=True)  # Ordenar del más reciente al más antiguo

# 📌 Función para limpiar backups antiguos y dejar solo los dos más recientes
def limpiar_backups():
    """ Elimina todos los backups dejando solo los dos más recientes, pero no borra si ambos son de hoy. """
    archivos_backup = obtener_archivos_backup()
    hoy = datetime.now().strftime("%Y%m%d")  # Obtener la fecha de hoy en formato AAAAMMDD

    if len(archivos_backup) == 2 and all(archivo[0].strftime("%Y%m%d") == hoy for archivo in archivos_backup):
        st.info("✅ No se han eliminado backups porque los dos más recientes son de hoy.")
    else:
        if len(archivos_backup) > 2:
            archivos_a_borrar = archivos_backup[2:]  # Mantener solo los dos más recientes
            for _, archivo in archivos_a_borrar:
                ruta_completa = os.path.join(BACKUP_DIR, archivo)
                os.remove(ruta_completa)
                st.warning(f"🗑️ Eliminado: {archivo}")

        st.success("✅ Limpieza completada. Se han mantenido los dos backups más recientes.")

    mostrar_tabla_backups()  # Llamamos a la función para mostrar la tabla después de limpiar

# 📌 Función para mostrar la tabla de backups
def mostrar_tabla_backups():
    """ Muestra una tabla con los archivos de backup en la carpeta """
    archivos_backup = obtener_archivos_backup()

    if not archivos_backup:
        st.warning("📁 La carpeta de backups está vacía.")
        return

    # Crear un DataFrame para mostrarlo como tabla en Streamlit
    df = pd.DataFrame(
        [(archivo[1], archivo[0].strftime("%Y-%m-%d %H:%M")) for archivo in archivos_backup],
        columns=["Archivo", "Fecha y Hora"]
    )

    # Mostrar la tabla en Streamlit
    st.markdown("### 📋 Lista de archivos en la carpeta backups:")
    st.dataframe(df)

# 📌 Función para realizar el backup
def hacer_backup():
    fecha_hora = datetime.now().strftime("%Y%m%d_%H%M")  # Obtener fecha y hora en formato requerido
    backup_file = os.path.join(BACKUP_DIR, f"FonotecaRadioUMH_backup_{fecha_hora}.db")
    
    # Simulación de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(1, 101):  # Simulación de proceso de backup
        time.sleep(0.02)  # Pequeña pausa para visualizar la barra de progreso
        progress_bar.progress(i)
        status_text.text(f"Realizando backup... {i}%")

    try:
        # Copiar la base de datos
        shutil.copy(DB_PATH, backup_file)
        status_text.text("✅ Backup completado con éxito.")
        st.success(f"✅ La copia de seguridad se ha guardado correctamente en `{backup_file}`.")
        return backup_file
    except Exception as e:
        st.error(f"❌ Error durante el backup: {e}")
        return None

# 📌 Interfaz de Streamlit
st.markdown("<h2 style='color: #BD2830; text-align: center;'>Backup de la Base de Datos</h2>", unsafe_allow_html=True)
st.write("Este módulo realiza un respaldo de la base de datos y permite descargarlo.")

# 🔹 Inicializar estado de sesión
if "backup_file" not in st.session_state:
    st.session_state.backup_file = None
if "mostrar_descarga" not in st.session_state:
    st.session_state.mostrar_descarga = False

# 🔹 Botón para iniciar el backup
if st.button("Hacer Backup", key="backup_button"):
    backup_file = hacer_backup()
    if backup_file:
        st.session_state.backup_file = backup_file
        st.session_state.mostrar_descarga = True  # Habilita la opción de descarga

        # 🔹 Llamamos a la limpieza de backups después del backup
        limpiar_backups()

# 🔹 Mostrar botón de descarga si hay un backup disponible
if st.session_state.mostrar_descarga and st.session_state.backup_file:
    st.markdown("### 📥 Descargar Backup")
    with open(st.session_state.backup_file, "rb") as file:
        btn_descarga = st.download_button(
            label="📥 Descargar el fichero de Backup",
            data=file,
            file_name=os.path.basename(st.session_state.backup_file),
            mime="application/octet-stream",
            key="download_button"
        )

    if btn_descarga:
        st.success("✅ La descarga del backup se ha realizado correctamente.")