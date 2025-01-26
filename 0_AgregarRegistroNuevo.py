import pandas as pd
import os

def agregar_registro(input_excel_path):
    """
    Permite al usuario agregar un nuevo registro a un archivo Excel existente.
    
    Args:
        input_excel_path (str): Ruta del archivo Excel.
    """
    try:
        # Verificar si el archivo Excel existe
        if not os.path.exists(input_excel_path):
            print(f"El archivo '{input_excel_path}' no existe. Creando uno nuevo.")
            df = pd.DataFrame(columns=["Nº", "AUTOR", "NOMBRE CD"])
        else:
            # Leer el archivo Excel
            df = pd.read_excel(input_excel_path)

        print("\n--- Añadir un nuevo registro ---")
        # Solicitar datos al usuario
        nuevo_numero = input("Introduce el Nº (por ejemplo, 0001): ").strip()
        nuevo_autor = input("Introduce el AUTOR: ").strip()
        nuevo_nombre_cd = input("Introduce el NOMBRE CD: ").strip()

        # Crear un nuevo registro como diccionario
        nuevo_registro = pd.DataFrame({
            "Nº": [nuevo_numero],
            "AUTOR": [nuevo_autor],
            "NOMBRE CD": [nuevo_nombre_cd]
        })

        # Concatenar el nuevo registro al DataFrame existente
        df = pd.concat([df, nuevo_registro], ignore_index=True)

        # Guardar el DataFrame actualizado de nuevo en el archivo Excel
        df.to_excel(input_excel_path, index=False)
        print(f"Registro añadido correctamente. Archivo actualizado: {input_excel_path}")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

# Ruta del archivo Excel
input_excel_path = "FONOTECA_CD_UMH.xlsx"

# Ejecutar la función
agregar_registro(input_excel_path)