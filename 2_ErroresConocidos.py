import pandas as pd

def update_excel_with_errors(base_excel_path, errors_excel_path, output_excel_path):
    """
    Actualiza los valores de "AUTOR" y "NOMBRE CD" en base a una Excel de errores conocida,
    asegurando el formato de la columna "Nº" y eliminando filas con "AUTOR" = "AUTOR".
    
    Args:
        base_excel_path (str): Ruta del archivo Excel base.
        errors_excel_path (str): Ruta del archivo Excel con errores conocidos.
        output_excel_path (str): Ruta donde se guardará el archivo Excel actualizado.
    """
    try:
        # Leer ambas hojas de Excel
        base_df = pd.read_excel(base_excel_path)
        errors_df = pd.read_excel(errors_excel_path)

        # Convertir la columna "Nº" a texto y formatear para que tengan el mismo número de dígitos
        base_df["Nº"] = base_df["Nº"].astype(str).str.zfill(4)  # Asegura 4 dígitos con ceros iniciales
        errors_df["Nº"] = errors_df["Nº"].astype(str).str.zfill(4)

        # Verificar si las columnas necesarias existen
        if {"Nº", "AUTOR_OK", "NOMBRE_CD_OK"}.issubset(errors_df.columns) and {"Nº", "AUTOR", "NOMBRE CD"}.issubset(base_df.columns):
            
            # Mostrar las primeras filas para verificar los datos cargados
            print("Datos del archivo base (primeras filas):")
            print(base_df.head())
            
            print("Datos del archivo de errores (primeras filas):")
            print(errors_df.head())
            
            # Combinar ambas tablas basándose en la columna "Nº"
            merged_df = base_df.merge(errors_df[["Nº", "AUTOR_OK", "NOMBRE_CD_OK"]], on="Nº", how="left")

            # Verificar coincidencias encontradas
            print("Registros con coincidencias encontradas (AUTOR_OK o NOMBRE_CD_OK no nulos):")
            print(merged_df[merged_df["AUTOR_OK"].notna() | merged_df["NOMBRE_CD_OK"].notna()])

            # Actualizar los valores de "AUTOR" y "NOMBRE CD" si hay datos en "AUTOR_OK" y "NOMBRE_CD_OK"
            merged_df["AUTOR"] = merged_df["AUTOR_OK"].combine_first(merged_df["AUTOR"])
            merged_df["NOMBRE CD"] = merged_df["NOMBRE_CD_OK"].combine_first(merged_df["NOMBRE CD"])

            # Eliminar columnas auxiliares
            merged_df.drop(columns=["AUTOR_OK", "NOMBRE_CD_OK"], inplace=True)

            # Eliminar filas donde "AUTOR" tenga el valor "AUTOR"
            merged_df = merged_df[merged_df["AUTOR"] != "AUTOR"]

            # Guardar el archivo actualizado
            merged_df.to_excel(output_excel_path, index=False)
            print(f"Archivo actualizado guardado en: {output_excel_path}")
        else:
            print("Las columnas requeridas no están presentes en uno de los archivos.")
    except Exception as e:
        print(f"Error al procesar los archivos: {e}")

# Rutas de los archivos
base_excel_path = "FONOTECA_CD_UMH.xlsx"  # Cambia esta ruta por tu archivo base
errors_excel_path = "FONOTECA_CD_UMH_ERRORES_CONOCIDOS.xlsx"  # Cambia esta ruta por tu archivo de errores
output_excel_path = "FONOTECA_CD_UMH_UPDATED.xlsx"  # Ruta para guardar el archivo actualizado

# Ejecutar la función
update_excel_with_errors(base_excel_path, errors_excel_path, output_excel_path)