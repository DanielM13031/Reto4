# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo requirements.txt al directorio de trabajo
COPY requirements.txt .

# Instala las dependencias del archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido de tu proyecto al directorio de trabajo
COPY . .

# Exponer el puerto en el que correrá la aplicación
EXPOSE 8050

# Comando para correr la aplicación usando Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:server"]
