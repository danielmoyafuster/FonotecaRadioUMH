import sqlite3
import streamlit as st
import time

# Ruta de la base de datos
DB_PATH = "./db/FonotecaRadioUMH.db"

def actualizar_imagenes_cd():
    """
    Recorre la tabla 'fonoteca_cd', busca registros con 'carátula_cd' vacío o NULL
    y los actualiza con la ruta './imagenes_cd/cd_[id].jpg'.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Seleccionar CDs sin imagen asignada
        cursor.execute("""
            SELECT id FROM fonoteca_cd
            WHERE carátula_cd IS NULL OR carátula_cd = ''
        """)
        cds_sin_imagen = cursor.fetchall()

        total_cds = len(cds_sin_imagen)
        if total_cds == 0:
            st.success("✅ No hay CDs sin imagen.")
            return

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Actualizar cada registro con la ruta de la imagen
        for idx, (cd_id,) in enumerate(cds_sin_imagen):
            nueva_ruta = f"./imagenes_cd/cd_{cd_id}.jpg"
            cursor.execute("""
                UPDATE fonoteca_cd
                SET carátula_cd = ?
                WHERE id = ?
            """, (nueva_ruta, cd_id))

            conn.commit()

            # Actualizar barra de progreso
            progress = (idx + 1) / total_cds
            progress_bar.progress(progress)
            status_text.text(f"Procesando {idx + 1} de {total_cds} CDs...")

            # Simular un pequeño retraso para visualización (opcional)
            time.sleep(0.1)

        st.success(f"✅ Se han actualizado {total_cds} registros en fonoteca_cd.")
        progress_bar.empty()  # Ocultar barra al finalizar
        status_text.empty()  # Limpiar mensaje

    except sqlite3.Error as e:
        st.error(f"❌ Error en la actualización: {e}")
    
    finally:
        if conn:
            conn.close()

# Streamlit UI
st.title("Actualizar Carátulas de CDs")
st.write("Este módulo actualiza las carátulas de los CDs sin imagen en la base de datos.")

if st.button("Actualizar carátulas de CDs"):
    actualizar_imagenes_cd()