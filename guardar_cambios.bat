@echo off
cd /d "%~dp0"

echo ============================================
echo   GUARDAR CAMBIOS EN GITHUB - GICA 2026
echo ============================================

:: Verificar si hay cambios
git status --porcelain > temp_status.txt
for %%A in (temp_status.txt) do if %%~zA==0 (
    del temp_status.txt
    echo No hay cambios nuevos para guardar.
    pause
    exit /b 0
)
del temp_status.txt

:: Pedir descripcion del cambio
echo.
set /p MENSAJE="Describe el cambio realizado: "
if "%MENSAJE%"=="" set MENSAJE="Actualizacion GICA %date% %time%"

:: Agregar todos los cambios de gica_app
git add gica_app/

:: Hacer commit
git commit -m "%MENSAJE%"

:: Subir a GitHub
echo.
echo Subiendo a GitHub...
git push origin master

if %ERRORLEVEL%==0 (
    echo.
    echo ✓ Cambios guardados exitosamente en GitHub.
) else (
    echo.
    echo ERROR al subir. Verifica tu conexion a internet.
)

echo.
pause
