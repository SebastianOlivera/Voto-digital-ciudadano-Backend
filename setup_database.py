import mysql.connector
from passlib.context import CryptContext
from datetime import datetime
import os

# Configuración de la base de datos
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'voting_db'
}

# Para generar hashes de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def execute_sql_file(cursor, file_path):
    """Ejecuta un archivo SQL"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read().split(';')
            for command in sql_commands:
                command = command.strip()
                if command:
                    cursor.execute(command)
        print(f"✓ Archivo {file_path} ejecutado exitosamente")
    except FileNotFoundError:
        print(f"⚠️ Archivo {file_path} no encontrado")
    except Exception as e:
        print(f"❌ Error ejecutando {file_path}: {e}")

def update_database_structure():
    """Actualiza la estructura de la base de datos"""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        print("Actualizando estructura de la base de datos...")
        
        # Verificar si las columnas ya existen en usuarios
        cursor.execute("DESCRIBE usuarios")
        columns = [column[0] for column in cursor.fetchall()]
        
        if 'circuito' not in columns:
            print("Agregando columna 'circuito'...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN circuito VARCHAR(10) NULL")
        
        if 'role' not in columns:
            print("Agregando columna 'role'...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN role VARCHAR(20) DEFAULT 'mesa'")
        
        # Verificar si las columnas ya existen en votos
        cursor.execute("DESCRIBE votos")
        voto_columns = [column[0] for column in cursor.fetchall()]
        
        if 'es_observado' not in voto_columns:
            print("Agregando columna 'es_observado'...")
            cursor.execute("ALTER TABLE votos ADD COLUMN es_observado BOOLEAN DEFAULT FALSE")
            
        if 'estado_validacion' not in voto_columns:
            print("Agregando columna 'estado_validacion'...")
            cursor.execute("ALTER TABLE votos ADD COLUMN estado_validacion VARCHAR(20) DEFAULT 'aprobado'")
            
        if 'circuito_mesa' not in voto_columns:
            print("Agregando columna 'circuito_mesa'...")
            cursor.execute("ALTER TABLE votos ADD COLUMN circuito_mesa VARCHAR(10) NULL")
        
        # Verificar si las columnas ya existen en autorizaciones
        cursor.execute("DESCRIBE autorizaciones")
        auth_columns = [column[0] for column in cursor.fetchall()]
        
        if 'es_autorizacion_especial' not in auth_columns:
            print("Agregando columna 'es_autorizacion_especial'...")
            cursor.execute("ALTER TABLE autorizaciones ADD COLUMN es_autorizacion_especial BOOLEAN DEFAULT FALSE")
        
        conn.commit()
        print("✅ Estructura de base de datos actualizada exitosamente!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_mock_data():
    """Crea datos mock para testing"""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        print("Creando datos mock...")
        
        # 1. Primero crear establecimientos y circuitos
        print("Creando establecimientos...")
        establecimientos = [
            ('Escuela Nacional No. 1', 'Montevideo', 'Montevideo', 'Centro', 'Ciudad Vieja', 'Sarandí 674', 'escuela', True),
            ('Liceo José Pedro Varela', 'Montevideo', 'Montevideo', 'Centro', 'Cordón', '18 de Julio 1234', 'liceo', True),
            ('Universidad de la República', 'Montevideo', 'Montevideo', 'Centro', 'Universidad', 'Av. 18 de Julio 1968', 'universidad', True),
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO establecimientos (nombre, departamento, ciudad, zona, barrio, direccion, tipo_establecimiento, accesible) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            establecimientos
        )
        
        print("Creando circuitos...")
        circuitos = [
            ('001', 'A', 1),
            ('002', 'B', 1), 
            ('003', 'C', 1),
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO circuitos (numero_circuito, numero_mesa, establecimiento_id) VALUES (%s, %s, %s)",
            circuitos
        )
        
        # 2. Limpiar usuarios existentes y crear nuevos
        cursor.execute("DELETE FROM usuarios")
        print("✓ Usuarios anteriores eliminados")
        
        # Hash real para "password123"
        password_hash = pwd_context.hash("password123")
        
        # 3. Usuarios de mesa con circuitos asignados (usar circuito_id)
        usuarios_mesa = [
            ("mesa001", password_hash, True, 1, "mesa"),
            ("mesa002", password_hash, True, 2, "mesa"),
            ("mesa003", password_hash, True, 3, "mesa"),
            ("presidente001", password_hash, True, 1, "presidente"),
            ("admin", password_hash, True, None, "superadmin"),
        ]
        
        cursor.executemany(
            "INSERT INTO usuarios (username, password_hash, is_active, circuito_id, role) VALUES (%s, %s, %s, %s, %s)",
            usuarios_mesa
        )
        print("✓ Usuarios de mesa creados")
        
        # 4. Partidos políticos
        partidos = [
            ("Frente Amplio", ),
            ("Partido Nacional", ),
            ("Partido Colorado", ),
            ("Cabildo Abierto", ),
            ("Partido Independiente", ),
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO partidos (nombre) VALUES (%s)",
            partidos
        )
        print("✓ Partidos políticos creados")
        
        # 5. Candidatos para elecciones generales (1 por partido)
        candidatos = [
            ("Yamandú Orsi", 1),           # Frente Amplio
            ("Álvaro Delgado", 2),         # Partido Nacional  
            ("Andrés Ojeda", 3),           # Partido Colorado
            ("Guido Manini Ríos", 4),     # Cabildo Abierto
            ("Pablo Mieres", 5),           # Partido Independiente
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO candidatos (nombre, partido_id) VALUES (%s, %s)",
            candidatos
        )
        print("✓ Candidatos creados")
        
        # 6. Autorizaciones de 200 votantes habilitados
        autorizaciones = []
        cedulas_votantes = []
        
        # Generar 200 cédulas únicas
        for i in range(200):
            cedula = f"1{str(i+1).zfill(7)}"  # Cédulas del 1000001 al 1000200
            circuito_id = (i % 3) + 1  # Distribuir entre circuitos 1, 2, 3
            mesa_usuario = f"mesa00{circuito_id}"
            
            autorizaciones.append((cedula, circuito_id, "HABILITADA", mesa_usuario, datetime.now(), None))
            cedulas_votantes.append(cedula)
        
        cursor.executemany(
            "INSERT IGNORE INTO autorizaciones (cedula, circuito_id, estado, autorizado_por, fecha_autorizacion, fecha_voto) VALUES (%s, %s, %s, %s, %s, %s)",
            autorizaciones
        )
        print("✓ 200 autorizaciones de votantes creadas")
        
        # 7. Votos reales de los 200 votantes autorizados
        votos_mock = []
        
        # Distribución de votos: 
        # Yamandú Orsi (id=1): 70 votos (35%)
        # Álvaro Delgado (id=2): 60 votos (30%)
        # Andrés Ojeda (id=3): 35 votos (17.5%)
        # Guido Manini Ríos (id=4): 20 votos (10%)
        # Pablo Mieres (id=5): 15 votos (7.5%)
        
        for i, cedula in enumerate(cedulas_votantes):
            circuito_id = (i % 3) + 1
            
            # Distribución de candidatos
            if i < 70:
                candidato_id = 1  # Yamandú Orsi
            elif i < 130:
                candidato_id = 2  # Álvaro Delgado
            elif i < 165:
                candidato_id = 3  # Andrés Ojeda
            elif i < 185:
                candidato_id = 4  # Guido Manini Ríos
            else:
                candidato_id = 5  # Pablo Mieres
            
            votos_mock.append((cedula, candidato_id, datetime.now(), circuito_id))
        
        cursor.executemany(
            "INSERT IGNORE INTO votos (cedula, candidato_id, timestamp, circuito_id) VALUES (%s, %s, %s, %s)",
            votos_mock
        )
        print("✓ 200 votos reales creados")
        
        conn.commit()
        print("🎉 Datos mock creados exitosamente!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def setup_complete_database():
    """Ejecuta la configuración completa de la base de datos"""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        print("🚀 Iniciando configuración completa de la base de datos...")
        
        # 1. Ejecutar estructura corregida
        execute_sql_file(cursor, 'create_correct_structure.sql')
        
        # 2. Actualizar estructura si es necesario
        update_database_structure()
        
        # 3. Insertar datos mock corregidos
        execute_sql_file(cursor, 'insert_correct_mock_data.sql')
        
        conn.commit()
        print("✅ Configuración completa de la base de datos finalizada!")
        print("\n🔑 Credenciales de prueba:")
        print("Usuario: presidente001, Contraseña: password123")
        print("Usuario: admin, Contraseña: password123")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def main():
    """Función principal que configura toda la base de datos"""
    print("=== CONFIGURADOR DE BASE DE DATOS ===")
    print("Creando estructura completa y datos mock...")
    
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        print("🚀 Iniciando configuración completa de la base de datos...")
        
        # 1. Actualizar estructura si es necesario
        print("Actualizando estructura de la base de datos...")
        
        # Verificar si las columnas ya existen en usuarios
        cursor.execute("DESCRIBE usuarios")
        columns = [column[0] for column in cursor.fetchall()]
        
        if 'circuito' not in columns:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN circuito VARCHAR(10) NULL")
        
        if 'role' not in columns:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN role VARCHAR(20) DEFAULT 'mesa'")
        
        # Verificar si las columnas ya existen en votos
        cursor.execute("DESCRIBE votos")
        voto_columns = [column[0] for column in cursor.fetchall()]
        
        if 'es_observado' not in voto_columns:
            cursor.execute("ALTER TABLE votos ADD COLUMN es_observado BOOLEAN DEFAULT FALSE")
            
        if 'estado_validacion' not in voto_columns:
            cursor.execute("ALTER TABLE votos ADD COLUMN estado_validacion VARCHAR(20) DEFAULT 'aprobado'")
            
        if 'circuito_mesa' not in voto_columns:
            cursor.execute("ALTER TABLE votos ADD COLUMN circuito_mesa VARCHAR(10) NULL")
        
        # Verificar si las columnas ya existen en autorizaciones
        cursor.execute("DESCRIBE autorizaciones")
        auth_columns = [column[0] for column in cursor.fetchall()]
        
        if 'es_autorizacion_especial' not in auth_columns:
            cursor.execute("ALTER TABLE autorizaciones ADD COLUMN es_autorizacion_especial BOOLEAN DEFAULT FALSE")
        
        print("✅ Estructura actualizada")
        
        # 2. Crear datos mock
        create_mock_data()
        
        conn.commit()
        print("✅ Configuración completa finalizada!")
        print("\n🔑 Credenciales de prueba:")
        print("Usuario: presidente001, Contraseña: password123")
        print("Usuario: admin, Contraseña: password123")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()