#!/bin/bash
# BehaviorLens Tunisia — Script de démarrage hackathon

echo "🚀 Démarrage BehaviorLens Tunisia..."
echo ""

# Backend
echo "▶  Backend FastAPI (port 8000)..."
cd "$(dirname "$0")/backend"
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/bl_backend.log 2>&1 &
BACK_PID=$!
sleep 3

# Vérifier backend
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
  echo "   ✓ Backend OK → http://localhost:8000"
  echo "   ✓ API Docs  → http://localhost:8000/docs"
else
  echo "   ✗ Backend failed — voir /tmp/bl_backend.log"
fi

# Frontend
echo ""
echo "▶  Frontend React (port 3000)..."
cd "$(dirname "$0")/frontend"
nohup ./node_modules/.bin/vite --port 3000 > /tmp/bl_frontend.log 2>&1 &
FRONT_PID=$!
sleep 4

# Vérifier frontend
if curl -s http://localhost:3000/ > /dev/null 2>&1; then
  echo "   ✓ Frontend OK → http://localhost:3000"
else
  echo "   ✗ Frontend failed — voir /tmp/bl_frontend.log"
fi

echo ""
echo "═══════════════════════════════════════"
echo "  BehaviorLens Tunisia — PRÊT !"
echo "═══════════════════════════════════════"
echo "  Dashboard : http://localhost:3000"
echo "  API Docs  : http://localhost:8000/docs"
echo "  Login     : admin@behaviorlens.tn"
echo "  Password  : admin123"
echo "═══════════════════════════════════════"
echo ""
echo "  Logs backend  : tail -f /tmp/bl_backend.log"
echo "  Logs frontend : tail -f /tmp/bl_frontend.log"
echo ""
echo "  Pour arrêter : kill $BACK_PID $FRONT_PID"
