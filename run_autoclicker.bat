@echo off
title AutoClicker PC Modpack
echo Iniciando AutoClicker PC...
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro ao executar o AutoClicker.
    pause
)
