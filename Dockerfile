# Paso 1: Imagen base con Python
FROM python:3.11.1

# Paso 2: Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Paso 3: Copiar el archivo de requisitos y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Paso 4: Copiar el resto del código fuente
COPY . /app

# Paso 5: Exponer el puerto en el que se ejecutará FastAPI
EXPOSE 8000

# Paso 6: Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
