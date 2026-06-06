"""
Migración: agrega el concepto de vigencia (año) a todas las tablas del sistema GICA.
Ejecutar una sola vez. Es seguro repetir: detecta si ya fue aplicada.
"""
import sqlite3
import os

DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'gica.db'))


def migrar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = OFF")

    try:
        # 1. Crear tabla vigencia
        conn.execute('''
            CREATE TABLE IF NOT EXISTS vigencia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                año INTEGER NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                descripcion TEXT DEFAULT '',
                activa INTEGER DEFAULT 0,
                fecha_inicio TEXT,
                fecha_cierre TEXT,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. Insertar vigencia 2026 si no hay ninguna
        if not conn.execute('SELECT id FROM vigencia LIMIT 1').fetchone():
            conn.execute('''
                INSERT INTO vigencia (año, nombre, descripcion, activa, fecha_inicio)
                VALUES (2026, 'GICA 2026', 'Vigencia inicial migrada del sistema', 1, '2026-01-01')
            ''')

        vid = conn.execute(
            'SELECT id FROM vigencia WHERE activa=1 ORDER BY año DESC LIMIT 1'
        ).fetchone()['id']

        # 3. Recrear ponderacion_proceso con UNIQUE(proceso_id, vigencia_id)
        cols = [c['name'] for c in conn.execute('PRAGMA table_info(ponderacion_proceso)').fetchall()]
        if 'vigencia_id' not in cols:
            conn.execute('''
                CREATE TABLE ponderacion_proceso_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proceso_id INTEGER REFERENCES proceso(id) ON DELETE CASCADE,
                    vigencia_id INTEGER REFERENCES vigencia(id) ON DELETE CASCADE,
                    proc_score REAL DEFAULT 0,
                    ind_score REAL DEFAULT 0,
                    car_score REAL DEFAULT 0,
                    norm_score REAL DEFAULT 0,
                    risk_score REAL DEFAULT 0,
                    fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(proceso_id, vigencia_id)
                )
            ''')
            conn.execute(f'''
                INSERT INTO ponderacion_proceso_v2
                    (proceso_id, vigencia_id, proc_score, ind_score,
                     car_score, norm_score, risk_score, fecha_actualizacion)
                SELECT proceso_id, {vid}, proc_score, ind_score,
                       car_score, norm_score, risk_score, fecha_actualizacion
                FROM ponderacion_proceso
            ''')
            conn.execute('DROP TABLE ponderacion_proceso')
            conn.execute('ALTER TABLE ponderacion_proceso_v2 RENAME TO ponderacion_proceso')
            print(f'  OK ponderacion_proceso migrada (vigencia_id={vid})')

        # 4. Agregar vigencia_id a las demás tablas
        for tabla in ['procedimiento', 'indicador', 'caracterizacion', 'normograma', 'riesgo']:
            cols = [c['name'] for c in conn.execute(f'PRAGMA table_info({tabla})').fetchall()]
            if 'vigencia_id' not in cols:
                conn.execute(f'ALTER TABLE {tabla} ADD COLUMN vigencia_id INTEGER REFERENCES vigencia(id)')
                conn.execute(f'UPDATE {tabla} SET vigencia_id={vid}')
                print(f'  OK {tabla}: vigencia_id agregada')
            else:
                print(f'  -- {tabla}: ya migrada')

        conn.commit()
        print(f'\nMigracion completada. Vigencia activa: ID={vid}')
        return vid

    except Exception as e:
        conn.rollback()
        print(f'ERROR en migracion: {e}')
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


if __name__ == '__main__':
    migrar()
