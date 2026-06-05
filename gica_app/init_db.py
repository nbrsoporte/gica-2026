"""Inicializa la base de datos y carga los datos del archivo Excel."""
import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'gica.db')


SCHEMA = """
CREATE TABLE IF NOT EXISTS rol (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    nivel INTEGER NOT NULL DEFAULT 4,
    descripcion TEXT DEFAULT '',
    puede_crear INTEGER DEFAULT 0,
    puede_editar INTEGER DEFAULT 0,
    puede_eliminar INTEGER DEFAULT 0,
    puede_admin_usuarios INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    nombre_completo TEXT NOT NULL,
    email TEXT DEFAULT '',
    password_hash TEXT NOT NULL,
    rol_id INTEGER REFERENCES rol(id) ON DELETE SET NULL,
    proceso_id INTEGER REFERENCES proceso(id) ON DELETE SET NULL,
    activo INTEGER DEFAULT 1,
    debe_cambiar_password INTEGER DEFAULT 0,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TEXT
);

CREATE TABLE IF NOT EXISTS log_auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER REFERENCES usuario(id) ON DELETE SET NULL,
    username TEXT DEFAULT '',
    accion TEXT NOT NULL,
    modulo TEXT DEFAULT '',
    detalle TEXT DEFAULT '',
    ip TEXT DEFAULT '',
    fecha TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tipo_proceso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    codigo TEXT NOT NULL,
    orden INTEGER DEFAULT 1,
    descripcion TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS unidad_organigrama (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    nivel TEXT DEFAULT 'Dependencia',
    responsable TEXT DEFAULT '',
    descripcion TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS proceso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL,
    nombre TEXT NOT NULL,
    tipo_proceso_id INTEGER REFERENCES tipo_proceso(id) ON DELETE SET NULL,
    unidad_id INTEGER REFERENCES unidad_organigrama(id) ON DELETE SET NULL,
    objetivo TEXT DEFAULT '',
    alcance TEXT DEFAULT '',
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ponderacion_proceso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proceso_id INTEGER UNIQUE REFERENCES proceso(id) ON DELETE CASCADE,
    proc_score REAL DEFAULT 0,
    ind_score REAL DEFAULT 0,
    car_score REAL DEFAULT 0,
    norm_score REAL DEFAULT 0,
    risk_score REAL DEFAULT 0,
    fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS procedimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proceso_id INTEGER REFERENCES proceso(id) ON DELETE CASCADE,
    codigo TEXT DEFAULT '',
    nombre TEXT NOT NULL,
    estado TEXT DEFAULT '1. BORRADOR',
    publicado_onedrive TEXT DEFAULT 'NO',
    descripcion TEXT DEFAULT '',
    responsable TEXT DEFAULT '',
    version TEXT DEFAULT '1.0',
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS indicador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proceso_id INTEGER REFERENCES proceso(id) ON DELETE CASCADE,
    codigo TEXT DEFAULT '',
    nombre TEXT NOT NULL,
    estado TEXT DEFAULT '1. BORRADOR',
    publicado_onedrive TEXT DEFAULT 'NO',
    formula TEXT DEFAULT '',
    meta TEXT DEFAULT '',
    unidad_medida TEXT DEFAULT '',
    frecuencia TEXT DEFAULT '',
    responsable TEXT DEFAULT '',
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS caracterizacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proceso_id INTEGER REFERENCES proceso(id) ON DELETE CASCADE,
    version TEXT DEFAULT '1.0',
    objetivo TEXT DEFAULT '',
    alcance TEXT DEFAULT '',
    proveedor TEXT DEFAULT '',
    entradas TEXT DEFAULT '',
    actividades TEXT DEFAULT '',
    salidas TEXT DEFAULT '',
    cliente TEXT DEFAULT '',
    recursos_humanos TEXT DEFAULT '',
    recursos_tecnologicos TEXT DEFAULT '',
    recursos_fisicos TEXT DEFAULT '',
    normatividad TEXT DEFAULT '',
    indicadores_ref TEXT DEFAULT '',
    riesgos_ref TEXT DEFAULT '',
    estado TEXT DEFAULT 'BORRADOR',
    fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS normograma (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proceso_id INTEGER REFERENCES proceso(id) ON DELETE CASCADE,
    tipo_norma TEXT DEFAULT 'Resolución',
    numero TEXT DEFAULT '',
    año TEXT DEFAULT '',
    entidad_expide TEXT DEFAULT '',
    titulo TEXT NOT NULL,
    descripcion TEXT DEFAULT '',
    fecha_expedicion TEXT,
    vigente INTEGER DEFAULT 1,
    enlace TEXT DEFAULT '',
    fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS riesgo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proceso_id INTEGER REFERENCES proceso(id) ON DELETE CASCADE,
    codigo TEXT DEFAULT '',
    nombre TEXT NOT NULL,
    descripcion TEXT DEFAULT '',
    tipo_riesgo TEXT DEFAULT 'Gestión',
    causa TEXT DEFAULT '',
    consecuencia TEXT DEFAULT '',
    probabilidad INTEGER DEFAULT 1,
    impacto INTEGER DEFAULT 1,
    nivel_riesgo TEXT DEFAULT 'Bajo',
    control_existente TEXT DEFAULT '',
    accion_mitigacion TEXT DEFAULT '',
    responsable TEXT DEFAULT '',
    fecha_identificacion TEXT,
    fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

TIPOS_PROCESO = [
    ('Apoyo', 'AP', 1, 'Procesos que brindan soporte a los demás procesos de la organización'),
    ('Estratégico', 'ES', 2, 'Procesos que orientan y controlan el rumbo estratégico de la entidad'),
    ('Misional', 'MI', 3, 'Procesos sustantivos que generan valor a los ciudadanos'),
    ('Evaluación', 'EV', 4, 'Procesos que evalúan y mejoran el desempeño organizacional'),
]

UNIDADES = [
    ('Secretario de Salud', 'Dirección', 'Secretario(a) de Salud', 'Máxima autoridad de la Secretaría de Salud'),
    ('Dirección administrativa y financiera', 'Subdirección', '', ''),
    ('Oficina asesora jurídica', 'Asesoría', '', ''),
    ('Oficina asesora de planeación', 'Asesoría', '', ''),
    ('Dirección de aseguramiento y prestación de servicios', 'Subdirección', '', ''),
    ('Dirección inspección vigilancia y control', 'Subdirección', '', ''),
    ('Dirección de salud pública', 'Subdirección', '', ''),
]

PROCESOS = [
    # (num, nombre, tipo_idx(0-based), unidad_idx(0-based), proc_score, ind_score, car_score, norm_score, risk_score)
    (1,  'GESTION DEL TALENTO HUMANO EN SALUD',                     0, 1, 0.8889, 1.0, 1.0, 1.0, 1.0),
    (2,  'GESTION ADMINISTRATIVA Y FINANCIERA EN SALUD',             0, 1, 0.9167, 1.0, 1.0, 1.0, 1.0),
    (3,  'GESTION JURIDICA EN SALUD',                                0, 2, 1.0,    1.0, 1.0, 1.0, 1.0),
    (4,  'DIRECCION SECTORIAL EN SALUD',                             1, 0, 0.0,    0.0, 0.0, 1.0, 1.0),
    (5,  'COORDINACION INTERSECTORIAL',                              1, 3, 0.0,    0.0, 1.0, 1.0, 1.0),
    (6,  'DESARROLLO DE CAPACIDADES',                                1, 3, 0.5,    0.5, 1.0, 1.0, 1.0),
    (7,  'PARTICIPACION SOCIAL',                                     1, 3, 0.9,    0.9, 1.0, 1.0, 1.0),
    (8,  'PLANEACION INTEGRAL SALUD',                                1, 3, 0.8,    0.76,1.0, 0.9, 1.0),
    (9,  'GESTION DE CONOCIMIENTO Y SISTEMA DE INFORMACION',         1, 3, 1.0,    1.0, 1.0, 1.0, 1.0),
    (10, 'GESTION INSTITUCIONAL CALIDAD',                            1, 3, 1.0,    1.0, 1.0, 1.0, 1.0),
    (11, 'GESTION DE LA PRESTACION DE SERVICIOS INDIVIDUALES',       2, 4, 1.0,    1.0, 1.0, 1.0, 1.0),
    (12, 'INSPECCION, VIGILANCIA Y CONTROL AL SISTEMA',              2, 5, 0.8,    0.8, 1.0, 1.0, 1.0),
    (13, 'GESTION DEL ASEGURAMIENTO EN SALUD',                       2, 4, 1.0,    1.0, 1.0, 1.0, 1.0),
    (14, 'GESTION EJES DEL PLAN DECENAL DE SALUD PUBLICA',           2, 6, 0.5714, 0.4, 1.0, 1.0, 1.0),
    (15, 'INSPECCION, VIGILANCIA Y CONTROL SANITARIO',               2, 6, 1.0,    1.0, 1.0, 1.0, 1.0),
    (16, 'VIGILANCIA EN SALUD PUBLICA',                              2, 6, 1.0,    1.0, 1.0, 1.0, 1.0),
    (17, 'GESTION DE INTERVENCIONES COLECTIVAS',                     2, 6, 1.0,    1.0, 1.0, 1.0, 1.0),
    (18, 'GESTION LABORATORIO SALUD PUBLICA',                        2, 6, 0.7,    1.0, 1.0, 1.0, 1.0),
    (19, 'EVALUACION CONTROL Y MEJORAMIENTO',                        3, 0, 1.0,    1.0, 1.0, 1.0, 1.0),
]

PROCEDIMIENTOS_INICIALES = [
    # (proceso_num, codigo, nombre, estado, publicado)
    (3,  'GJ-PR-01', 'PROCEDIMIENTO TUTELAS', '3. EN REVISION LIDER Y/O GICA', 'NO'),
    (3,  'GJ-PR-02', 'PROCEDIMIENTOS DERECHO DE PETICION', '3. EN REVISION LIDER Y/O GICA', 'NO'),
    (3,  'GJ-PR-03', 'PROCEDIMIENTOS CONSULTAS', '3. EN REVISION LIDER Y/O GICA', 'NO'),
    (3,  'GJ-PR-04', 'PROCEDIMIENTO ACTOS ADMINISTRATIVOS', '3. EN REVISION LIDER Y/O GICA', 'NO'),
    (7,  'PS-PR-01', 'PROCEDIMIENTO IMPLEMENTACION POLITICAS DE PARTICIPACION SOCIAL EN SALUD', '3. EN REVISION LIDER Y/O GICA', 'NO'),
    (7,  'PS-PR-02', 'PROCEDIMIENTO ASISTENCIAS TECNICAS IMPLEMENTACION POLITICAS DE PARTICIPACION SOCIAL EN SALUD', '2. EN CONSTRUCCION  (NUEVO)', 'NO'),
    (7,  'PS-PR-03', 'PROCEDIMIENTO PLAN DE ACCION POLITICAS DE PARTICIPACION SOCIAL EN SALUD', '2. EN CONSTRUCCION  (NUEVO)', 'NO'),
    (8,  'PI-PR-01', 'PROCEDIMIENTO FORMULACION DEL PLAN TERRITORIAL EN SALUD', '3. EN REVISION LIDER Y/O GICA', 'NO'),
    (8,  'PI-PR-02', 'PROCEDIMIENTO MONITOREO Y EVALUACION DEL PLAN TERRITORIAL EN SALUD', '3. EN REVISION LIDER Y/O GICA', 'NO'),
    (9,  'GC-PR-01', 'PROCEDIMIENTO 1 ASISTENCIA TECNICA', '4. ACTUALIZADO ', 'NO'),
    (9,  'GC-PR-02', 'PROCEDIMIENTO 2 SOPORTE TECNICO EQUIPOS DE COMPUTO', '4. ACTUALIZADO ', 'NO'),
    (9,  'GC-PR-03', 'PROCEDIMIENTO 3 GESTION INTEGRAL DE ESTADISTICAS VITALES', '4. ACTUALIZADO ', 'NO'),
    (9,  'GC-PR-04', 'PROCEDIMIENTO 4 ACTUALIZACION DE TRAMITES EN LA PLATAFORMA SUIT', '4. ACTUALIZADO ', 'NO'),
    (9,  'GC-PR-05', 'PROCEDIMIENTO 5 SEGUIMIENTO AL REPORTE DE INFORMACION EN LOS SISTEMAS DE INFORMACION EN SALUD', '4. ACTUALIZADO ', 'NO'),
    (9,  'GC-PR-06', 'PROCEDIMIENTO 6 CARGUE ANEXO TECNICO RESOLUCION 202 DE 2021', '4. ACTUALIZADO ', 'NO'),
    (9,  'GC-PR-07', 'PROCEDIMIENTO 7 REPORTE DE LOS RIPS DE LA POBLACION POBRE NO ASEGURADA - PPNA - RESOLUCION 2275 DE 2023', '4. ACTUALIZADO ', 'NO'),
    (9,  'GC-PR-08', 'PROCEDIMIENTO 8 GESTION DEL CONOCIMIENTO', '4. ACTUALIZADO ', 'NO'),
    (9,  'GC-PR-09', 'PROCEDIMIENTO 9 GESTION DEL MICROSITIO WEB DE LA SECRETARIA DE SALUD DEPARTAMENTAL', '4. ACTUALIZADO ', 'NO'),
    (5,  'CI-PR-01', 'PROCEDIMIENTO SEGUIMIENTO, MONITOREO Y EVALUACION DE PLANES DE ACCION DE POLITICAS PUBLICAS DE SALUD EN EL DEPARTAMENTO DE BOLIVAR', '2. EN CONSTRUCCION  (NUEVO)', 'NO'),
    (15, 'GS-IVC SA-PR-01', 'IVC SANITARIO DE ALIMENTOS Y BEBIDAS CON ENFOQUE EN RIESGOS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-PR-02', 'INSCRIPCION Y DILIGENCIAMIENTO DEL FORMATO DE REPORTE', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-PR-03', 'DESINFECCION CAVAS PARA TRANSPORTE DE MUESTRAS DE ALIMENTOS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-PR-04', 'TRANSPORTE Y ENTREGA MUESTRAS AL LABORATORIO DEPARTAMENTAL', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-PR-05', 'IVC MEDICAMENTOS A ESTABLECIMIENTOS FARMACEUTICOS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-PR-06', 'ALMACENAMIENTO DE MEDICAMENTOS DE CONTROL ESPECIAL', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-PR-07', 'DESNATURALIZACION E INCINERACION DE MEDICAMENTOS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-PR-08', 'INSPECCION VIGILANCIA Y CONTROL DE FACTORES DE RIESGO ASOCIADOS AL AMBIENTE', '4. ACTUALIZADO ', 'NO'),
]

INDICADORES_INICIALES = [
    (15, 'GS-IVC SA-IND 01', 'INDICADOR MUNICIPIOS PROGRAMADOS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 02', 'INDICADOR MUNICIPIOS CON CONCEPTOS SANITARIOS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 03', 'INDICADOR DE DESARROLLO DE CAPACIDADES MPM REALIZADAS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 04', 'INDICADOR NUMERO DE INSTITUCIONES EDUCATIVAS CON PAE', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 05', 'INDICADOR VISITAS REALIZADAS A BODEGAS DE PRODUCTOS IMPORTADOS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 06', 'INDICADOR TOMA DE MUESTRA DE ALIMENTOS REALIZADAS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 07', 'INDICADOR SANCIONATORIO', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 08', 'INDICADOR PUESTOS DE CONTROL REALIZADOS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 09', 'INDICADOR PREPARACION DE SITIOS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 10', 'INDICADOR NUMERO DE NOTIFICACIONES DE ETA', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 11', 'INDICADOR NUMERO DE IVC RECIBIDAS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 12', 'INDICADOR MUNICIPIOS VISITADOS', '4. ACTUALIZADO ', 'NO'),
    (15, 'GS-IVC SA-IND 13', 'INDICADOR COBERTURA AUTORIZACIONES SANITARIAS EXPENDIOS CARNES', '4. ACTUALIZADO ', 'NO'),
]

NORMOGRAMA_INICIAL = [
    (3,  'Ley', '270', '1996', 'Congreso de Colombia', 'Ley Estatutaria de la Administración de Justicia', 'Regula la administración de justicia', '1996-03-07', 1, ''),
    (3,  'Ley', '1755', '2015', 'Congreso de Colombia', 'Derecho de petición', 'Regula el ejercicio del derecho fundamental de petición', '2015-06-30', 1, ''),
    (1,  'Decreto', '1083', '2015', 'Presidencia de la República', 'Decreto Único Reglamentario del Sector de Función Pública', 'Compila las normas del sector función pública', '2015-05-26', 1, ''),
    (2,  'Resolución', '2674', '2013', 'Ministerio de Salud y Protección Social', 'Requisitos sanitarios que deben cumplir las personas naturales y/o jurídicas que ejercen actividades de fabricación, procesamiento, preparación, envase, almacenamiento, transporte, distribución y comercialización de alimentos', 'Requisitos sanitarios de alimentos', '2013-07-22', 1, ''),
    (15, 'Resolución', '1229', '2013', 'Ministerio de Salud y Protección Social', 'Modelo de inspección, vigilancia y control sanitario para los productos de uso y consumo humano', 'Marco del IVC sanitario', '2013-04-30', 1, ''),
    (15, 'Ley', '9', '1979', 'Congreso de Colombia', 'Código Sanitario Nacional', 'Normas generales que servirán de base a las disposiciones y reglamentaciones necesarias para preservar, restaurar u mejorar las condiciones necesarias en lo que se relaciona a la salud humana', '1979-01-16', 1, ''),
    (10, 'Decreto', '1011', '2006', 'Presidencia de la República', 'Sistema Obligatorio de Garantía de Calidad en Salud - SOGCS', 'Establece el SOGCS para las entidades que hacen parte del Sistema General de Seguridad Social en Salud', '2006-04-03', 1, ''),
    (10, 'Resolución', '1446', '2006', 'Ministerio de la Protección Social', 'Sistema de información para la calidad', 'Define el sistema de información para la calidad del SOGCS', '2006-05-08', 1, ''),
    (14, 'Resolución', '1841', '2013', 'Ministerio de Salud y Protección Social', 'Plan Decenal de Salud Pública 2012-2021', 'Adopta el Plan Decenal de Salud Pública', '2013-05-28', 1, ''),
    (19, 'Decreto', '943', '2014', 'Presidencia de la República', 'Actualización del Modelo Estándar de Control Interno - MECI', 'Actualiza el MECI para entidades del Estado', '2014-05-21', 1, ''),
]

RIESGOS_INICIALES = [
    (3, 'GJ-R-01', 'Incumplimiento de términos en respuesta a tutelas', 'Riesgo de no dar respuesta oportuna a acciones de tutela', 'Jurídico', 'Falta de coordinación entre dependencias', 'Sanciones disciplinarias y multas', 3, 4, 'Extremo', 'Seguimiento semanal de términos', 'Implementar sistema de alertas tempranas', 'Jefe Oficina Jurídica'),
    (7, 'PS-R-01', 'Baja participación comunitaria', 'Riesgo de no alcanzar metas de participación social', 'Gestión', 'Desconocimiento de la comunidad sobre espacios de participación', 'Incumplimiento de metas del PDSP', 3, 3, 'Alto', 'Convocatorias previas', 'Estrategia de comunicación y difusión', 'Coordinador de Participación Social'),
    (15, 'IVC-R-01', 'Ingreso de alimentos contaminados al mercado', 'Riesgo de que alimentos no aptos lleguen a los consumidores', 'Salud Pública', 'Limitaciones en capacidad de inspección', 'Brotes de enfermedades transmitidas por alimentos', 2, 5, 'Extremo', 'Visitas de IVC programadas', 'Incrementar frecuencia de visitas a puntos críticos', 'Director de Salud Pública'),
    (14, 'PDSP-R-01', 'Desactualización de indicadores del PDSP', 'Riesgo de reportar información desactualizada de los ejes del PDSP', 'Gestión', 'Falta de sistemas de información integrados', 'Toma de decisiones con información incorrecta', 3, 3, 'Alto', 'Comités de seguimiento trimestrales', 'Automatización de reportes de indicadores', 'Director de Salud Pública'),
    (19, 'ECM-R-01', 'Incumplimiento del plan de mejoramiento', 'Riesgo de no ejecutar las acciones correctivas planteadas', 'Gestión', 'Falta de recursos o priorización', 'Hallazgos recurrentes en auditorías', 2, 4, 'Alto', 'Seguimiento mensual', 'Reuniones de seguimiento con líderes de proceso', 'Jefe de Control Interno'),
]


def init():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    for tp in TIPOS_PROCESO:
        conn.execute('INSERT INTO tipo_proceso (nombre, codigo, orden, descripcion) VALUES (?,?,?,?)', tp)

    unidad_ids = []
    for u in UNIDADES:
        cur = conn.execute('INSERT INTO unidad_organigrama (nombre, nivel, responsable, descripcion) VALUES (?,?,?,?)', u)
        unidad_ids.append(cur.lastrowid)

    tipo_ids = [row[0] for row in conn.execute('SELECT id FROM tipo_proceso ORDER BY orden').fetchall()]

    proceso_map = {}
    for p in PROCESOS:
        num, nombre, tipo_idx, unidad_idx, ps, is_, cs, ns, rs = p
        codigo = f'P{num:02d}'
        cur = conn.execute(
            'INSERT INTO proceso (codigo, nombre, tipo_proceso_id, unidad_id) VALUES (?,?,?,?)',
            (codigo, nombre, tipo_ids[tipo_idx], unidad_ids[unidad_idx]))
        pid = cur.lastrowid
        proceso_map[num] = pid
        conn.execute(
            'INSERT INTO ponderacion_proceso (proceso_id, proc_score, ind_score, car_score, norm_score, risk_score) VALUES (?,?,?,?,?,?)',
            (pid, ps, is_, cs, ns, rs))

    for pr in PROCEDIMIENTOS_INICIALES:
        p_num, codigo, nombre, estado, pub = pr
        conn.execute(
            'INSERT INTO procedimiento (proceso_id, codigo, nombre, estado, publicado_onedrive) VALUES (?,?,?,?,?)',
            (proceso_map[p_num], codigo, nombre, estado, pub))

    for ind in INDICADORES_INICIALES:
        p_num, codigo, nombre, estado, pub = ind
        conn.execute(
            'INSERT INTO indicador (proceso_id, codigo, nombre, estado, publicado_onedrive) VALUES (?,?,?,?,?)',
            (proceso_map[p_num], codigo, nombre, estado, pub))

    for n in NORMOGRAMA_INICIAL:
        p_num = n[0]
        conn.execute('''
            INSERT INTO normograma (proceso_id, tipo_norma, numero, año, entidad_expide, titulo, descripcion, fecha_expedicion, vigente, enlace)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        ''', (proceso_map[p_num], n[1], n[2], n[3], n[4], n[5], n[6], n[7], n[8], n[9]))

    for r in RIESGOS_INICIALES:
        p_num = r[0]
        conn.execute('''
            INSERT INTO riesgo (proceso_id, codigo, nombre, descripcion, tipo_riesgo, causa, consecuencia, probabilidad, impacto, nivel_riesgo, control_existente, accion_mitigacion, responsable)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (proceso_map[p_num], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12]))

    # ── ROLES ──────────────────────────────────────────────────────────────
    ROLES = [
        # (nombre, nivel, descripcion, puede_crear, puede_editar, puede_eliminar, puede_admin_usuarios)
        ('Administrador',     1, 'Acceso total al sistema y gestión de usuarios', 1, 1, 1, 1),
        ('Líder GICA',        2, 'Gestiona todos los módulos de calidad, sin administrar usuarios', 1, 1, 1, 0),
        ('Líder de Proceso',  3, 'Edita información de su proceso asignado', 1, 1, 0, 0),
        ('Consultor',         4, 'Solo lectura en todos los módulos', 0, 0, 0, 0),
    ]
    rol_map = {}
    for r in ROLES:
        cur = conn.execute(
            'INSERT INTO rol (nombre, nivel, descripcion, puede_crear, puede_editar, puede_eliminar, puede_admin_usuarios) VALUES (?,?,?,?,?,?,?)', r)
        rol_map[r[0]] = cur.lastrowid

    # ── USUARIOS INICIALES ──────────────────────────────────────────────────
    USUARIOS = [
        # (username, nombre_completo, email, password, rol_nombre, debe_cambiar)
        ('admin',       'Administrador del Sistema',       'admin@saluddpto.gov.co',   'Admin@2026!',   'Administrador',    0),
        ('lider.gica',  'Líder GICA Secretaría de Salud',  'gica@saluddpto.gov.co',    'Gica@2026!',    'Líder GICA',       1),
        ('consultor',   'Usuario Consulta',                'consulta@saluddpto.gov.co','Consulta@2026!','Consultor',        0),
    ]
    for u in USUARIOS:
        username, nombre, email, pwd, rol_nombre, debe_cambiar = u
        conn.execute('''
            INSERT INTO usuario (username, nombre_completo, email, password_hash, rol_id, debe_cambiar_password)
            VALUES (?,?,?,?,?,?)
        ''', (username, nombre, email, generate_password_hash(pwd), rol_map[rol_nombre], debe_cambiar))

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")
    print(f"  - {len(TIPOS_PROCESO)} tipos de proceso")
    print(f"  - {len(UNIDADES)} unidades de organigrama")
    print(f"  - {len(PROCESOS)} procesos")
    print(f"  - {len(PROCEDIMIENTOS_INICIALES)} procedimientos")
    print(f"  - {len(INDICADORES_INICIALES)} indicadores")
    print(f"  - {len(NORMOGRAMA_INICIAL)} normas")
    print(f"  - {len(RIESGOS_INICIALES)} riesgos")
    print(f"  - {len(ROLES)} roles")
    print(f"  - {len(USUARIOS)} usuarios")
    print()
    print("  Credenciales iniciales:")
    for u in USUARIOS:
        print(f"    Usuario: {u[0]:15s}  Contraseña: {u[3]:15s}  Rol: {u[4]}")


if __name__ == '__main__':
    init()
