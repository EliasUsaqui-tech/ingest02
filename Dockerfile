FROM python:3.11-slim

WORKDIR /programas/ingesta

# Instalar dependencias de Python
RUN pip install --no-cache-dir boto3 pandas pymysql

# Copiar el código
COPY . .

# Comando de ejecución
CMD ["python3", "./ingesta.py"]
