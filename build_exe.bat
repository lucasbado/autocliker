@echo off
title Criando Executavel Windows (.exe) - AutoClicker PC
echo ========================================================
echo Criando arquivo AutoClicker_PC.exe standalone...
echo ========================================================
cd /d "%~dp0"
python -m PyInstaller --noconsole --onefile --name "AutoClicker_PC" main.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo SUCESSO! O arquivo AutoClicker_PC.exe foi gerado na pasta:
    echo %~dp0dist\AutoClicker_PC.exe
    echo ========================================================
) else (
    echo.
    echo Ocorreu um erro ao gerar o executavel .exe.
)
pause
