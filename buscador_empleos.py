name: Agente Buscador de Empleos SIG

on:
  schedule:
    # Se ejecuta de lunes a viernes a las 12:00 UTC
    - cron: '0 12 * * 1-5'
  workflow_dispatch:  # Esto añade un botón para ejecutarlo a mano

jobs:
  run-scraper:
    runs-on: ubuntu-latest

    steps:
      - name: Clonar el repositorio
        uses: actions/checkout@v4

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Instalar dependencias
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Ejecutar el agente
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        run: python buscador_empleos.py
