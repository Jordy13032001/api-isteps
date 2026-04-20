#!/usr/bin/env bash
# Script de build para Railway

set -o errexit  # Detener si hay errores

echo "🔧 Instalando dependencias..."
pip install -r requirements.txt

echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "🗄️ Ejecutando migraciones..."
python manage.py migrate --no-input

echo "✅ Build completado!"
