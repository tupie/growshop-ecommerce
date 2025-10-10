#!/usr/bin/env bash
set -e

echo "🔧 [sync_project] Sincronizando proyecto local..."

# Asegurarse de estar en la raíz
cd "$(dirname "$0")"

# Backend locks
if [ -d "backend" ]; then
  echo "📦 Actualizando locks Python..."
  source backend/.venv/bin/activate
  pip freeze > backend/requirements.lock
  deactivate
fi

# Frontend locks
if [ -d "frontend" ]; then
  echo "📦 Actualizando locks Node..."
  cd frontend
  npm ci
  npm dedupe
  npm audit fix --force || true
  cd ..
fi

# Backups ligeros
echo "🗂️ Creando backup local..."
tar czf backups_$(date +%Y%m%d_%H%M).tar.gz backend/frontend 2>/dev/null || echo "⚠️ No se creó backup"

echo "✅ Sincronización local completa"
