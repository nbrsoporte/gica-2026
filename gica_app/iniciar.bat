@echo off
cd /d "%~dp0"
echo ============================================
echo   SISTEMA GICA - Secretaria de Salud
echo   Gestion Institucional de la Calidad
echo ============================================
echo.

if not exist gica.db (
    echo Inicializando base de datos...
    python init_db.py
    echo.
) else (
    echo Verificando tablas de seguridad...
    python migrar_seguridad.py
    echo.
)

echo Iniciando servidor web...
echo Abra su navegador en: http://localhost:5000
echo.
echo  Credenciales de acceso:
echo  - admin       / Admin@2026!     (Administrador)
echo  - lider.gica  / Gica@2026!      (Lider GICA)
echo  - consultor   / Consulta@2026!  (Solo lectura)
echo.
echo Presione Ctrl+C para detener el servidor.
echo.
python app.py
pause
