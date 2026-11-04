#!/usr/bin/env bash
# Construcción en Render: se ejecuta desde la raíz del repositorio con `bash build.sh`.
set -o errexit

echo "Node $(node --version), npm $(npm --version)"

pip install -r backend/requirements.txt

# --include=dev: Vite es dependencia de desarrollo y no se instalaría con NODE_ENV=production.
npm ci --include=dev --prefix frontend
npm run build --prefix frontend

cd backend
python manage.py collectstatic --no-input
python manage.py migrate --no-input
