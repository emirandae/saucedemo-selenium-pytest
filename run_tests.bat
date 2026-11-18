@echo off
REM ==========================================================================
REM  Ejecuta la suite de pruebas automatizadas de SauceDemo en Windows.
REM  1) Localiza Python  2) Crea el entorno virtual .venv  3) Instala dependencias
REM  4) Ejecuta pytest   5) Abre el reporte HTML generado en reports\
REM  Argumentos opcionales se pasan a pytest, por ejemplo:
REM     run_tests.bat --browser edge
REM     run_tests.bat --headless -m humo
REM ==========================================================================
setlocal
cd /d "%~dp0"

set "PY_EXE="
set "PY_ARGS="
where py >nul 2>nul && (set "PY_EXE=py" & set "PY_ARGS=-3")
if not defined PY_EXE if exist "%USERPROFILE%\anaconda3\python.exe" set "PY_EXE=%USERPROFILE%\anaconda3\python.exe"
if not defined PY_EXE if exist "%ProgramData%\anaconda3\python.exe" set "PY_EXE=%ProgramData%\anaconda3\python.exe"
if not defined PY_EXE if exist "%USERPROFILE%\miniconda3\python.exe" set "PY_EXE=%USERPROFILE%\miniconda3\python.exe"
if not defined PY_EXE (
    python -c "import sys" >nul 2>nul && set "PY_EXE=python"
)
if not defined PY_EXE (
    echo [ERROR] No se encontro Python 3. Instalelo desde https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creando entorno virtual .venv ...
    "%PY_EXE%" %PY_ARGS% -m venv .venv || goto :error
)

echo [2/3] Instalando dependencias ...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt || goto :error

echo [3/3] Ejecutando pruebas ...
".venv\Scripts\python.exe" -m pytest %*
set "RC=%ERRORLEVEL%"

if exist "reports\reporte.html" start "" "reports\reporte.html"
echo.
echo Resultados: reports\reporte.html, reports\resultados.json, reports\resultados.csv y reports\capturas\
echo Codigo de salida de pytest: %RC%  (0 = todas aprobadas, 1 = hay pruebas fallidas)
pause
exit /b %RC%

:error
echo [ERROR] No se pudo preparar el entorno. Revise el mensaje anterior.
pause
exit /b 1
