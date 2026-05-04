@echo off
echo Iniciando Frontend de Cliente (Servidor estático)...
cd frontend\cliente\static
python -m http.server 3000