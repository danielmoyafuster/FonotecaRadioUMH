import camelot
import pandas as pd

def extract_tables_with_camelot(pdf_path, excel_output_path):
    """
    Extrae tablas de un PDF usando Camelot y las consolida en un solo archivo Excel.
    Args:
        pdf_path (str): Ruta del archivo PDF.
        excel_output_path (str): Ruta donde se guardará el archivo Excel.
    """
    try:
        # Extraer tablas del PDF usando Camelot
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")

        if tables.n > 0:
            # Combinar todas las tablas en un solo DataFrame
            combined_data = pd.concat([table.df for table in tables], ignore_index=True)

            # Asignar nombres a las columnas si es posible
            combined_data.columns = ["Nº", "AUTOR", "NOMBRE CD"]

            # Exportar el DataFrame consolidado a un archivo Excel
            combined_data.to_excel(excel_output_path, index=False)
            print(f"Archivo Excel generado correctamente en: {excel_output_path}")
        else:
            print("No se encontraron tablas en el PDF.")

    except Exception as e:
        print(f"Error al procesar el PDF con Camelot: {e}")

# Rutas de ejemplo
pdf_path = "FONOTECA_CD_UMH.pdf"  # Cambia esto a la ruta de tu archivo PDF
excel_output_path = "FONOTECA_CD_UMH.xlsx"  # Cambia esto a donde quieras guardar el archivo Excel

# Ejecutar la función
extract_tables_with_camelot(pdf_path, excel_output_path)