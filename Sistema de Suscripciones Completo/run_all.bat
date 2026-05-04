@echo off
echo Iniciando Sistema de Gestión de Suscripciones...
echo.

echo Iniciando Backend (FastAPI)...
start "" cmd /k "cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 > nul

echo Iniciando Frontend de Cliente (Servidor estático)...
start "" cmd /k "cd frontend\cliente\static && python -m http.server 3000"

timeout /t 2 > nul

echo Iniciando Frontend de Admin (Servidor estático)...
start "" cmd /k "cd frontend\admin && python -m http.server 3001"

echo.
echo Sistema iniciado:
echo - Backend API disponible en: http://localhost:8000
echo - Documentación API en: http://localhost:8000/docs
echo - Frontend Cliente disponible en: http://localhost:3000
echo - Frontend Admin disponible en: http://localhost:3001
echo.
echo Presiona Ctrl+C en cualquiera de las ventanas para detener los servidores
pause