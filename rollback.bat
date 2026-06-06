@echo off
cd /d "%~dp0"

echo ============================================
echo   ROLLBACK / RECUPERAR VERSION - GICA 2026
echo ============================================
echo.
echo Versiones disponibles:
git tag -l
echo.
echo Commits recientes:
git log --oneline -10
echo.
echo ============================================
echo OPCIONES:
echo   1. Volver a la version estable v1.0-estable
echo   2. Volver a un commit especifico
echo   3. Cancelar
echo ============================================
echo.
set /p OPCION="Elige una opcion (1/2/3): "

if "%OPCION%"=="1" (
    echo.
    echo Restaurando version estable v1.0-estable...
    git checkout v1.0-estable -- gica_app/
    git add gica_app/
    git commit -m "rollback: restaurado a v1.0-estable"
    git push origin master
    echo ✓ Proyecto restaurado a version estable.
)

if "%OPCION%"=="2" (
    echo.
    set /p HASH="Ingresa el ID del commit (primeros 7 caracteres): "
    git checkout %HASH% -- gica_app/
    git add gica_app/
    git commit -m "rollback: restaurado al commit %HASH%"
    git push origin master
    echo ✓ Proyecto restaurado al commit %HASH%.
)

if "%OPCION%"=="3" (
    echo Operacion cancelada.
)

echo.
pause
