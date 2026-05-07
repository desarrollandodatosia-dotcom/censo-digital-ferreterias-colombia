@echo off
title CEMANTIX — Cementos Argos
cd /d "C:\Users\CORE 7 5050\Downloads\Etapa3"
echo.
echo  =============================================
echo   CEMANTIX — Inteligencia de Mercado Argos
echo  =============================================
echo.
echo  Iniciando app en http://localhost:8501
echo  Presiona Ctrl+C para detener.
echo.
streamlit run app.py
pause
