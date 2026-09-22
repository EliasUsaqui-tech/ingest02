import boto3
import pymysql
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN MYSQL ---
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'ingesta_user')
DB_PASS = os.getenv('DB_PASS', 'Ingesta2026!')
DB_NAME = os.getenv('DB_NAME', 'ingesta_db')
TABLE_NAME = os.getenv('TABLE_NAME', 'clientes')

# --- CONFIGURACIÓN S3 ---
nombreBucket = os.getenv('S3_BUCKET', 'grc-data-1u')


def extraer_datos_mysql():
    """Conecta a MySQL, lee toda una tabla y devuelve un DataFrame."""
    print(f"Conectando a MySQL en {DB_HOST}:{DB_PORT}...")
    conexion = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

    query = f"SELECT * FROM {TABLE_NAME}"
    print(f"Ejecutando: {query}")

    df = pd.read_sql(query, conexion)
    conexion.close()

    print(f"✅ {len(df)} registros extraídos de la tabla '{TABLE_NAME}'")
    return df


def guardar_csv(df):
    """Guarda el DataFrame en un archivo CSV con timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ficheroUpload = f"datos_{timestamp}.csv"
    df.to_csv(ficheroUpload, index=False)
    print(f"✅ Archivo guardado localmente: {ficheroUpload}")
    return ficheroUpload


def subir_a_s3(ficheroUpload):
    """Sube el archivo CSV al bucket S3."""
    print(f"Subiendo '{ficheroUpload}' al bucket '{nombreBucket}'...")
    s3 = boto3.client('s3')
    s3.upload_file(ficheroUpload, nombreBucket, ficheroUpload)
    print(f"✅ Archivo '{ficheroUpload}' subido exitosamente a S3")


if __name__ == "__main__":
    try:
        # 1. Extraer de MySQL
        df = extraer_datos_mysql()

        if df.empty:
            print("⚠️  No hay datos para procesar.")
        else:
            # 2. Guardar como CSV
            ficheroUpload = guardar_csv(df)

            # 3. Subir a S3
            subir_a_s3(ficheroUpload)

            print("\n🎉 Ingesta completada con éxito")

    except Exception as e:
        print(f"❌ Error durante la ingesta: {e}")
        raise
