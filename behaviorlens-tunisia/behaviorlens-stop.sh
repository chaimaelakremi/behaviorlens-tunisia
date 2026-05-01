#!/bin/bash
# BehaviorLens Tunisia — Stop

echo "Arrêt de BehaviorLens Tunisia..."

pkill -f "uvicorn main:app" 2>/dev/null && echo "  ✓ Backend arrêté" || echo "  — Backend non actif"
pkill -f "vite --port 3000"  2>/dev/null && echo "  ✓ Frontend arrêté" || echo "  — Frontend non actif"
rm -f /tmp/behaviorlens/pids

echo "Arrêté."
