#!/bin/bash
# BehaviorLens Tunisia — Launcher
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
LOG_DIR="/tmp/behaviorlens"
BACKEND_PORT=8000
FRONTEND_PORT=3000

mkdir -p "$LOG_DIR"

# ── Vérifier si déjà en cours ────────────────────────────────────────────────
already_running() {
    curl -s "http://localhost:$1/" > /dev/null 2>&1
}

notify() {
    # Notification bureau si disponible
    which notify-send > /dev/null 2>&1 && notify-send "BehaviorLens Tunisia" "$1" --icon=applications-internet 2>/dev/null || true
}

# ── Arrêter les anciens processus ────────────────────────────────────────────
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "vite --port $FRONTEND_PORT" 2>/dev/null || true
sleep 1

# ── Backend ──────────────────────────────────────────────────────────────────
echo "[1/3] Démarrage Backend..."
cd "$BACKEND_DIR"
nohup uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT \
    > "$LOG_DIR/backend.log" 2>&1 &
BACK_PID=$!

# Attendre que le backend réponde
for i in $(seq 1 15); do
    sleep 1
    if curl -s "http://localhost:$BACKEND_PORT/" > /dev/null 2>&1; then
        echo "   ✓ Backend démarré (PID $BACK_PID)"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "   ✗ Backend n'a pas démarré — voir $LOG_DIR/backend.log"
        exit 1
    fi
done

# ── Frontend ─────────────────────────────────────────────────────────────────
echo "[2/3] Démarrage Frontend..."
cd "$FRONTEND_DIR"
nohup ./node_modules/.bin/vite --port $FRONTEND_PORT \
    > "$LOG_DIR/frontend.log" 2>&1 &
FRONT_PID=$!

for i in $(seq 1 15); do
    sleep 1
    if curl -s "http://localhost:$FRONTEND_PORT/" > /dev/null 2>&1; then
        echo "   ✓ Frontend démarré (PID $FRONT_PID)"
        break
    fi
done

# Sauvegarder les PIDs
echo "$BACK_PID $FRONT_PID" > "$LOG_DIR/pids"

# ── Ouvrir le navigateur ─────────────────────────────────────────────────────
echo "[3/3] Ouverture du dashboard..."
sleep 1
google-chrome --app="http://localhost:$FRONTEND_PORT" \
    --window-size=1400,900 \
    --window-position=50,50 \
    --title="BehaviorLens Tunisia" \
    > /dev/null 2>&1 &

notify "Framework démarré — Dashboard ouvert"
echo ""
echo "════════════════════════════════════════"
echo "  BehaviorLens Tunisia — EN COURS"
echo "════════════════════════════════════════"
echo "  Dashboard : http://localhost:$FRONTEND_PORT"
echo "  API       : http://localhost:$BACKEND_PORT/docs"
echo "  Login     : admin@behaviorlens.tn"
echo "  Password  : admin123"
echo "════════════════════════════════════════"
echo "  Logs : $LOG_DIR/"
echo "  Stop : ~/hackaton/behaviorlens-tunisia/behaviorlens-stop.sh"
echo "════════════════════════════════════════"
