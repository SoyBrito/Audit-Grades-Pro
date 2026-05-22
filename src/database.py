import sqlite3
from datetime import datetime

class GestorBaseDatos:
    def __init__(self, nombre_db="audit_grades.db"):
        self.nombre_db = nombre_db
        self.inicializar_base_datos()

    def conectar(self):
        """ Retorna una conexión activa a la base de datos """
        return sqlite3.connect(self.nombre_db)

    def inicializar_base_datos(self):
        """ Crea las tablas y los Triggers de inmutabilidad (Catedral Digital) """
        conexion = self.conectar()
        cursor = conexion.cursor()

        # 1. Tabla de Calificaciones (US3.1)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calificaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id TEXT NOT NULL,
                materia TEXT NOT NULL,
                nota REAL NOT NULL,
                profesor_id TEXT NOT NULL,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. Tabla de Auditoría Inmutable (US3.3)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auditoria_notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operacion TEXT NOT NULL,
                calificacion_id INTEGER,
                usuario_id TEXT,
                nota_anterior REAL,
                nota_nueva REAL,
                fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 3. TRIGGER: Auditoría automática al modificar
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS trg_audit_update
            AFTER UPDATE ON calificaciones
            BEGIN
                INSERT INTO auditoria_notas 
                (operacion, calificacion_id, usuario_id, nota_anterior, nota_nueva)
                VALUES 
                ('UPDATE', NEW.id, NEW.profesor_id, OLD.nota, NEW.nota);
            END;
        ''')

        conexion.commit()
        conexion.close()

    # --- Operaciones Transaccionales (CRUD) ---

    def registrar_nota(self, estudiante_id, materia, nota, profesor_id):
        """ Inserta una nota nueva aplicando validaciones estrictas. """
        try:
            nota_float = float(nota)
            if not (0 <= nota_float <= 20):
                raise ValueError("La nota debe estar comprendida entre 0 y 20.")

            conexion = self.conectar()
            cursor = conexion.cursor()
            
            cursor.execute('''
                INSERT INTO calificaciones (estudiante_id, materia, nota, profesor_id)
                VALUES (?, ?, ?, ?)
            ''', (estudiante_id, materia, nota_float, profesor_id))
            
            conexion.commit()
            conexion.close()
            return True, "Nota registrada exitosamente en el sistema."

        except ValueError as e:
            return False, f"Error de validación: {e}"
        except sqlite3.Error as e:
            return False, f"Error crítico de base de datos: {e}"

    def modificar_nota(self, calificacion_id, nueva_nota, profesor_id):
        """ Modifica un registro. La auditoría se delega al Trigger de SQLite. """
        try:
            nota_float = float(nueva_nota)
            if not (0 <= nota_float <= 20):
                raise ValueError("La nota debe estar comprendida entre 0 y 20.")

            conexion = self.conectar()
            cursor = conexion.cursor()
            
            cursor.execute('''
                UPDATE calificaciones 
                SET nota = ?, profesor_id = ?
                WHERE id = ?
            ''', (nota_float, profesor_id, calificacion_id))
            
            conexion.commit()
            conexion.close()
            return True, "Modificación ejecutada. Registro de auditoría generado."

        except ValueError as e:
            return False, str(e)
        except sqlite3.Error as e:
            return False, "Error interno al procesar la modificación en la base de datos."

    def consultar_auditoria(self):
        """ Extrae el historial inmutable completo. """
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM auditoria_notas ORDER BY fecha_cambio DESC")
        registros = cursor.fetchall()
        conexion.close()
        return registros

    def buscar_calificaciones(self, criterio=""):
        """ Aplica filtros de búsqueda para la tabla de la interfaz gráfica. """
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        if criterio:
            query = '''
                SELECT id, estudiante_id, materia, nota 
                FROM calificaciones 
                WHERE estudiante_id LIKE ? OR materia LIKE ?
            '''
            param = f"%{criterio}%"
            cursor.execute(query, (param, param))
        else:
            cursor.execute("SELECT id, estudiante_id, materia, nota FROM calificaciones")
            
        resultados = cursor.fetchall()
        conexion.close()
        return resultados