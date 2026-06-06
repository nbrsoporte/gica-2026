# Sistema GICA 2026 — Instrucciones de Uso

**Gestión Institucional de la Calidad**
Secretaría de Salud Departamental de Bolívar

---

## Requisitos Previos

- **Python 3.10+** instalado
- **pip** (incluido con Python)
- Sin dependencias externas adicionales (usa SQLite embebido)

---

## Instalación y Ejecución

### Opción 1 — Inicio automático (recomendado)

Haga doble clic en el archivo:
```
gica_app/iniciar.bat
```
El script verifica si la base de datos existe, la inicializa si es necesario, y lanza el servidor Flask.

### Opción 2 — Manual desde terminal

```bash
# 1. Instalar dependencias (solo la primera vez)
cd gica_app
pip install -r requirements.txt

# 2. Inicializar la base de datos (solo la primera vez)
python init_db.py

# 3. Iniciar el servidor
python app.py
```

Abrir el navegador en: **http://localhost:5000**

---

## Credenciales de Acceso Iniciales

| Rol | Usuario | Contraseña | Permisos |
|:---|:---|:---|:---|
| **Administrador** | `admin` | `Admin@2026!` | Acceso total + gestión de usuarios |
| **Líder GICA** | `lider.gica` | `Gica@2026!` | Gestión de calidad, sin administrar usuarios |
| **Consultor** | `consultor` | `Consulta@2026!` | Solo lectura |

> **Nota de seguridad:** Al iniciar sesión por primera vez, el sistema solicitará cambiar la contraseña.

---

## Módulos del Sistema

### Tablero GICA (Dashboard)
- Semáforo de avance por proceso: Verde (≥90%), Amarillo (70-89%), Rojo (<70%)
- **Indicador de Avance Global GICA** con barra de progreso
- Gráfico de barras horizontal por proceso
- Gráfico de dona con distribución del semáforo
- **Exportar tablero a Excel** con colores de semáforo

### Procesos
- 19 procesos institucionales organizados por tipo (Apoyo, Estratégico, Misional, Evaluación)
- Vista de detalle con todos los módulos del proceso
- Ponderación en 5 dimensiones: Procedimientos, Indicadores, Caracterización, Normograma, Mapa de Riesgos
- Cada dimensión se califica de 0 a 1 (0% a 100%)

### Procedimientos
- Registro de procedimientos por proceso
- Estados: Borrador, En Construcción, En Revisión, Actualizado
- Control de publicación en OneDrive, versión y responsable

### Indicadores
- Registro de indicadores por proceso
- Campos: fórmula, meta, unidad de medida, frecuencia y responsable

### Caracterización de Procesos
- Ficha SIPOC: proveedor, entradas, actividades, salidas, cliente
- Recursos: humanos, tecnológicos, físicos
- Normatividad y referencias a indicadores y riesgos

### Normograma
- Marco normativo por proceso (leyes, decretos, resoluciones)
- Control de vigencia y enlace al documento oficial

### Mapa de Riesgos
- Valoración en matriz 5×5 (Probabilidad × Impacto)
- Nivel automático: Bajo, Moderado, Alto, Extremo
- Control existente y acción de mitigación
- **Exportar mapa de riesgos a Excel** con colores por nivel

### Organigrama
- Unidades de la Secretaría de Salud con nivel jerárquico y responsable

### Búsqueda Global
- Campo de búsqueda en la barra superior
- Busca simultáneamente en procesos, procedimientos, indicadores, normograma y riesgos

### Administración (solo Administrador)
- **Usuarios:** crear, editar, activar/desactivar, eliminar
- **Roles:** configurar niveles de acceso y permisos
- **Auditoría:** log completo de todas las acciones con filtros por usuario, acción y rango de fechas
- **Exportar auditoría a Excel**

---

## Seguridad Implementada

- **Autenticación por sesión** con contraseñas encriptadas (Werkzeug/bcrypt)
- **4 niveles de acceso:** Administrador, Líder GICA, Líder de Proceso, Consultor
- **Cambio obligatorio de contraseña** en el primer acceso
- **Log de auditoría completo** — cada acción registra usuario, módulo, detalle, IP y fecha
- **Modal de confirmación** antes de eliminar cualquier registro
- **Secret key** almacenada en archivo `.env` (no expuesta en el código)
- **Páginas de error** personalizadas (404 y 500)

---

## Estructura de Archivos

```
Control de calidad/
├── gica_app/
│   ├── app.py                  ← Servidor Flask + todas las rutas (~1.500 líneas)
│   ├── init_db.py              ← Inicializa la BD con datos precargados
│   ├── migrar_seguridad.py     ← Migración de tablas de seguridad
│   ├── iniciar.bat             ← Script de arranque (doble clic para ejecutar)
│   ├── requirements.txt        ← Dependencias Python
│   ├── .env                    ← Variables de entorno (NO compartir)
│   ├── .env.example            ← Plantilla de variables de entorno
│   ├── gica.db                 ← Base de datos SQLite
│   ├── templates/
│   │   ├── base.html           ← Layout principal (sidebar, topbar, modal, alertas)
│   │   ├── dashboard.html      ← Tablero con semáforo y gráficos
│   │   ├── buscar.html         ← Resultados de búsqueda global
│   │   ├── errors/             ← Páginas de error 404 y 500
│   │   ├── auth/               ← Login, perfil, cambio de contraseña
│   │   ├── admin/              ← Usuarios, roles, auditoría
│   │   ├── procesos/           ← Lista, detalle, formulario, ponderación
│   │   ├── procedimientos/     ← CRUD de procedimientos
│   │   ├── indicadores/        ← CRUD de indicadores
│   │   ├── caracterizacion/    ← CRUD de caracterizaciones
│   │   ├── normograma/         ← CRUD del marco normativo
│   │   ├── riesgos/            ← CRUD del mapa de riesgos
│   │   ├── tipos_proceso/      ← CRUD de tipos de proceso
│   │   └── organigrama/        ← CRUD del organigrama
│   └── static/                 ← CSS y JS adicionales
├── guardar_cambios.bat         ← Guarda cambios en Git (commit)
├── rollback.bat                ← Deshace el último cambio (Git)
└── INSTRUCCIONES_DE_USO.md    ← Este archivo
```

---

## Dependencias Python

| Paquete | Versión | Uso |
|:---|:---|:---|
| Flask | ≥2.3.0 | Framework web |
| Werkzeug | ≥2.3.0 | Seguridad de contraseñas |
| openpyxl | ≥3.1.0 | Exportación a Excel |
| python-dotenv | ≥1.0.0 | Variables de entorno |

---

## Notas Importantes

- La base de datos `gica.db` se crea automáticamente al ejecutar `init_db.py`
- El archivo `.env` contiene la clave secreta del sistema — **no lo comparta ni lo suba al repositorio**
- Para hacer una copia de seguridad, basta con guardar el archivo `gica.db`
- Para reiniciar la base de datos desde cero, elimine `gica.db` y ejecute `python init_db.py`
- El servidor corre en modo desarrollo (`debug=True`) — en producción use un servidor WSGI como Gunicorn
