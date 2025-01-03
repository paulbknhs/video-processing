# Basis-Image: Python 3.9
FROM python:3.9-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# System-Abhängigkeiten installieren (inkl. FFmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungsdateien kopieren
COPY app.py .
COPY static/ static/
COPY templates/ templates/

# Erstelle notwendige Verzeichnisse
RUN mkdir uploads processed

# Port freigeben
EXPOSE 8080

# Umgebungsvariablen setzen
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Anwendung starten
CMD ["python", "app.py"] 