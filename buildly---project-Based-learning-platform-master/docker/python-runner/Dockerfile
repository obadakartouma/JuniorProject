FROM python:3.11-slim

WORKDIR /app

# Sicherheitsuser
RUN useradd -m runner
USER runner

CMD ["python3", "main.py"]