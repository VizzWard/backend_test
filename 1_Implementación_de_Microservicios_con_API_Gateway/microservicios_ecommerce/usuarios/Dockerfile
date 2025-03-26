FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Puerto para exponer
EXPOSE 8000

# Comando para ejecutar
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]