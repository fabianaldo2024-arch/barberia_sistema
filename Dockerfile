FROM python:3.11-slim

# Evita que Python genere .pyc y fuerza salida sin buffer (logs en tiempo real)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema (ajusta si usas Poetry en vez de pip)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero requirements para aprovechar la cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# El comando real (runserver, celery worker, celery beat) se define
# por servicio en docker-compose.yml, así que aquí dejamos un default.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]