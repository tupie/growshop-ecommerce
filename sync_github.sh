#!/usr/bin/env bash
set -e

echo "🔄 [sync_github] Sincronizando entorno con GitHub..."

# Asegurarse de estar en la raíz del proyecto
cd "$(dirname "$0")"

# Limpieza de archivos temporales y compilados
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +

# Validar estado del repo
git status
read -p "¿Deseas continuar con el push? (y/N): " confirm
[ "$confirm" != "y" ] && echo "❌ Cancelado" && exit 1

# Commit automático con fecha y usuario
USER_NAME=$(git config user.name)
DATE=$(date +"%Y-%m-%d %H:%M")
git add .
git commit -m "chore(sync): actualización manual por ${USER_NAME:-desconocido} (${DATE})" || echo "ℹ️ Nada nuevo para commitear"

# Push
git pull --rebase origin main || true
git push origin main

echo "✅ Repositorio sincronizado con GitHub"
