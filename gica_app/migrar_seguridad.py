"""Agrega tablas de seguridad a la base de datos existente sin borrar datos."""
import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'gica.db')

TABLAS_SEGURIDAD = """
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
"""

ROLES = [
    ('Administrador',     1, 'Acceso total al sistema y gestión de usuarios', 1, 1, 1, 1),
    ('Líder GICA',        2, 'Gestiona todos los módulos de calidad, sin administrar usuarios', 1, 1, 1, 0),
    ('Líder de Proceso',  3, 'Edita información de su proceso asignado', 1, 1, 0, 0),
    ('Consultor',         4, 'Solo lectura en todos los módulos', 0, 0, 0, 0),
]

USUARIOS = [
    ('admin',       'Administrador del Sistema',       'admin@saluddpto.gov.co',   'Admin@2026!',   'Administrador',    0),
    ('lider.gica',  'Líder GICA Secretaría de Salud',  'gica@saluddpto.gov.co',    'Gica@2026!',    'Líder GICA',       1),
    ('consultor',   'Usuario Consulta',                'consulta@saluddpto.gov.co','Consulta@2026!','Consultor',        0),
]


def migrar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # Crear tablas de seguridad
    conn.executescript(TABLAS_SEGURIDAD)
    print("Tablas de seguridad creadas/verificadas.")

    # Insertar roles si no existen
    rol_map = {}
    for r in ROLES:
        existente = conn.execute('SELECT id FROM rol WHERE nombre=?', (r[0],)).fetchone()
        if existente:
            rol_map[r[0]] = existente['id']
            print(f"  Rol '{r[0]}' ya existe (ID:{existente['id']})")
        else:
            cur = conn.execute(
                'INSERT INTO rol (nombre, nivel, descripcion, puede_crear, puede_editar, puede_eliminar, puede_admin_usuarios) VALUES (?,?,?,?,?,?,?)', r)
            rol_map[r[0]] = cur.lastrowid
            print(f"  Rol '{r[0]}' creado (ID:{cur.lastrowid})")

    # Insertar usuarios si no existen
    for u in USUARIOS:
        username, nombre, email, pwd, rol_nombre, debe_cambiar = u
        existente = conn.execute('SELECT id FROM usuario WHERE username=?', (username,)).fetchone()
        if existente:
            print(f"  Usuario '{username}' ya existe.")
        else:
            conn.execute('''
                INSERT INTO usuario (username, nombre_completo, email, password_hash, rol_id, debe_cambiar_password)
                VALUES (?,?,?,?,?,?)
            ''', (username, nombre, email, generate_password_hash(pwd), rol_map[rol_nombre], debe_cambiar))
            print(f"  Usuario '{username}' creado (rol: {rol_nombre})")

    conn.commit()
    conn.close()
    print("\nMigración completada exitosamente.")
    print("\nCredenciales de acceso:")
    for u in USUARIOS:
        print(f"  Usuario: {u[0]:15s}  Contraseña: {u[3]:15s}  Rol: {u[4]}")


if __name__ == '__main__':
    migrar()
