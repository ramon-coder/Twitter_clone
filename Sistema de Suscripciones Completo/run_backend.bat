@echo off
echo Iniciando Backend de Gestión de Suscripciones (FastAPI)...
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000