@echo off
REM Script de setup para Windows

echo.
echo ==========================================
echo ChatRAG - Setup Automatizado (Windows)
echo ==========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Python no está instalado o no está en el PATH.
    echo Por favor, instala Python desde: https://www.python.org/
    echo Durante la instalación, marca la opción "Add Python to PATH"
    pause
    exit /b 1
)

echo Python encontrado: 
python --version
echo.

REM Crear entorno virtual
echo 📦 Creando entorno virtual...
python -m venv venv

REM Activar entorno virtual
echo 🔌 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📥 Instalando dependencias...
python -m pip install --upgrade pip

REM Limpiar versiones conflictivas por si el entorno virtual ya existía
pip uninstall google google-generativeai google-genai -y
pip install -r requirements.txt

REM Crear .env desde .env.example si no existe
if not exist .env (
    echo  Creando archivo .env...
    copy .env.example .env
    echo.
    echo   IMPORTANTE: Edita el archivo .env y pega tu GEMINI_API_KEY
    echo   Ve a: https://ai.google.dev/ para obtener tu API key
) else (
    echo  Archivo .env ya existe
)

echo.
echo ==========================================
echo ✅ Setup completado!
echo ==========================================
echo.
echo Próximos pasos:
echo 1. Edita el archivo .env y pega tu GEMINI_API_KEY
echo 2. Ejecuta la app: python src/ui/main_ui.py
echo.
echo Para activar el entorno en futuras sesiones, ejecuta:
echo    venv\Scripts\activate.bat
echo.
pause
