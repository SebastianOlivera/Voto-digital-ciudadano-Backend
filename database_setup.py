import mysql.connector
from passlib.context import CryptContext
from datetime import datetime
import os

# Configuración de la base de datos
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'user'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'voting_db')
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
    """Crea datos mock directamente en código"""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        print("Creando datos mock completos...")
        
        # Limpiar tablas en orden correcto (respetando foreign keys)
        cursor.execute("DELETE FROM votos")
        cursor.execute("DELETE FROM autorizaciones") 
        cursor.execute("DELETE FROM usuarios")
        cursor.execute("DELETE FROM candidatos")
        cursor.execute("DELETE FROM partidos")
        cursor.execute("DELETE FROM circuitos")
        cursor.execute("DELETE FROM establecimientos")
        print("✓ Tablas limpiadas")
        
        # 1. Crear establecimientos
        establecimientos = [
            ('Escuela Nacional No. 1', 'Montevideo', 'Montevideo', 'Centro', 'Ciudad Vieja', 'Sarandí 674', 'escuela', True),
            ('Liceo José Pedro Varela', 'Montevideo', 'Montevideo', 'Centro', 'Cordón', '18 de Julio 1234', 'liceo', True),
            ('Universidad de la República', 'Montevideo', 'Montevideo', 'Centro', 'Universidad', 'Av. 18 de Julio 1968', 'universidad', True),
            ('Escuela No. 45', 'Montevideo', 'Montevideo', 'Este', 'Pocitos', 'Av. Brasil 2567', 'escuela', True),
            ('Escuela Artigas', 'Montevideo', 'Montevideo', 'Oeste', 'Cerro', 'Carlos María Ramírez 1456', 'escuela', True),
            ('Escuela Rural No. 45', 'Canelones', 'Las Piedras', 'Norte', 'Barrio Nuevo', 'Ruta 5 Km 25', 'escuela', False),
            ('Liceo de Canelones', 'Canelones', 'Canelones', 'Centro', 'Centro', 'Treinta y Tres 123', 'liceo', True),
            ('Escuela de Pando', 'Canelones', 'Pando', 'Este', 'Centro', 'Leandro Gómez 789', 'escuela', True),
            ('Instituto Santa Lucía', 'Canelones', 'Santa Lucía', 'Sur', 'Centro', 'José Batlle y Ordóñez 456', 'instituto', True),
            ('Liceo de Punta del Este', 'Maldonado', 'Punta del Este', 'Península', 'Centro', 'Gorlero 456', 'liceo', True),
            ('Instituto Maldonado', 'Maldonado', 'Maldonado', 'Centro', 'Centro', 'Sarandí 234', 'instituto', False),
            ('Escuela de San Carlos', 'Maldonado', 'San Carlos', 'Norte', 'Centro', 'Artigas 345', 'escuela', True),
            ('Escuela de Colonia', 'Colonia', 'Colonia del Sacramento', 'Histórico', 'Barrio Histórico', 'Calle de los Suspiros 12', 'escuela', False),
            ('Liceo de Rosario', 'Colonia', 'Rosario', 'Centro', 'Centro', 'General Artigas 567', 'liceo', True),
            ('Liceo de Rocha', 'Rocha', 'Rocha', 'Centro', 'Centro', '19 de Abril 678', 'liceo', True),
            ('Escuela de Chuy', 'Rocha', 'Chuy', 'Frontera', 'Centro', 'Av. Brasil 890', 'escuela', False),
            ('Liceo Departamental Rivera', 'Rivera', 'Rivera', 'Centro', 'Centro', 'Sarandí 123', 'liceo', True),
            ('Escuela de Tranqueras', 'Rivera', 'Tranqueras', 'Rural', 'Centro', 'Ruta 5 Km 463', 'escuela', False),
            ('Liceo José Pedro Varela', 'Salto', 'Salto', 'Centro', 'Centro', 'Uruguay 456', 'liceo', True),
            ('Escuela de Constitución', 'Salto', 'Constitución', 'Norte', 'Centro', 'Artigas 789', 'escuela', True),
            ('Liceo No. 1 Paysandú', 'Paysandú', 'Paysandú', 'Centro', 'Centro', '18 de Julio 234', 'liceo', True),
            ('Escuela de Guichón', 'Paysandú', 'Guichón', 'Este', 'Centro', 'General Flores 567', 'escuela', False),
            ('Liceo de Mercedes', 'Soriano', 'Mercedes', 'Centro', 'Centro', 'Giménez 345', 'liceo', True),
            ('Liceo de Tacuarembó', 'Tacuarembó', 'Tacuarembó', 'Centro', 'Centro', 'Wilson Ferreira 678', 'liceo', True),
        ]
        
        cursor.executemany(
            "INSERT INTO establecimientos (nombre, departamento, ciudad, zona, barrio, direccion, tipo_establecimiento, accesible) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            establecimientos
        )
        print("✓ Establecimientos creados")
        
        # 2. Crear circuitos
        circuitos = [
            ('001', 'A', 1), ('002', 'B', 1), ('003', 'C', 1),
            ('004', 'A', 2), ('005', 'B', 2), ('006', 'A', 3),
            ('007', 'A', 4), ('008', 'B', 4), ('009', 'A', 5),
            ('010', 'A', 5),  # Added missing circuit 010
            ('016', 'A', 6), ('017', 'B', 6), ('018', 'A', 7),
            ('019', 'A', 8), ('020', 'A', 9), ('026', 'A', 10),
            ('027', 'A', 11), ('028', 'A', 12), ('036', 'A', 13),
            ('037', 'A', 14), ('041', 'A', 15), ('042', 'A', 16),
            ('051', 'A', 17), ('052', 'A', 18), ('061', 'A', 19),
            ('062', 'A', 20), ('071', 'A', 21), ('072', 'A', 22),
            ('081', 'A', 23), ('091', 'A', 24),
        ]
        
        cursor.executemany(
            "INSERT INTO circuitos (numero_circuito, numero_mesa, establecimiento_id) VALUES (%s, %s, %s)",
            circuitos
        )
        print("✓ Circuitos creados")
        
        # Clear credenciales_autorizadas and add some examples
        cursor.execute("DELETE FROM credenciales_autorizadas")
        print("✓ Tabla credenciales_autorizadas limpiada")
        
        # Agregar credenciales específicas por circuito
        credenciales_por_circuito = [
            # Circuito 001
            ('12345671', 1), ('12345672', 1), ('12345673', 1), ('12345674', 1), ('12345675', 1),
            # Circuito 002
            ('22345671', 2), ('22345672', 2), ('22345673', 2), ('22345674', 2), ('22345675', 2),
            # Circuito 003
            ('32345671', 3), ('32345672', 3), ('32345673', 3), ('32345674', 3), ('32345675', 3),
        ]
        
        cursor.executemany(
            "INSERT INTO credenciales_autorizadas (cedula, circuito_id) VALUES (%s, %s)",
            credenciales_por_circuito
        )
        print("✓ Credenciales específicas por circuito creadas")
        
        # 3. Crear partidos
        partidos = [
            ('Frente Amplio',), ('Partido Nacional',), ('Partido Colorado',), ('Cabildo Abierto',), ('Partido Independiente',)
        ]
        cursor.executemany("INSERT INTO partidos (nombre) VALUES (%s)", partidos)
        print("✓ Partidos creados")
        
        # 4. Crear candidatos
        candidatos = [
            ('Yamandú Orsi', 1), ('Álvaro Delgado', 2), ('Andrés Ojeda', 3), 
            ('Guido Manini Ríos', 4), ('Pablo Mieres', 5)
        ]
        cursor.executemany("INSERT INTO candidatos (nombre, partido_id) VALUES (%s, %s)", candidatos)
        print("✓ Candidatos creados")
        
        # 5. Crear usuarios con hash correcto
        password_hash = pwd_context.hash("password123")
        usuarios = [
            ("mesa001", password_hash, True, 1, "mesa"),
            ("mesa002", password_hash, True, 2, "mesa"),
            ("mesa003", password_hash, True, 3, "mesa"),
            ("presidente001", password_hash, True, 1, "presidente"),
            ("presidente002", password_hash, True, 2, "presidente"),
            ("presidente003", password_hash, True, 3, "presidente"),
            ("admin", password_hash, True, 1, "superadmin"),
        ]
        
        cursor.executemany(
            "INSERT INTO usuarios (username, password_hash, is_active, circuito_id, role) VALUES (%s, %s, %s, %s, %s)",
            usuarios
        )
        print("✓ Usuarios creados")
        
        # 6. Crear 100 votos de ejemplo
        import random
        votos = []
        
        # Generar 100 votos con distribución realista
        for i in range(100):
            cedula = f"{random.randint(10000000, 99999999)}"
            # Distribución de votos: 70% candidatos, 20% blanco (NULL), 10% anulado (es_anulado=True)
            rand = random.random()
            if rand < 0.7:
                candidato_id = random.randint(1, 5)  # Candidatos 1-5
                es_anulado = False
            elif rand < 0.9:
                candidato_id = None  # Voto en blanco (NULL)
                es_anulado = False
            else:
                candidato_id = random.randint(1, 5)  # Candidato cualquiera pero anulado
                es_anulado = True
                
            circuito_id = random.choice([1, 2, 3, 16, 17, 18, 26, 27, 28])
            es_observado = random.random() < 0.05  # 5% de votos observados
            
            votos.append((cedula, candidato_id, circuito_id, es_observado, 'aprobado', es_anulado))
        
        # Agregar algunos votos específicos para testing
        votos.extend([
            ('87654321', 1, 1, False, 'aprobado', False),
            ('88888888', 1, 2, False, 'aprobado', False),
            ('12341234', 2, 3, False, 'aprobado', False),
        ])
        
        cursor.executemany(
            "INSERT INTO votos (cedula, candidato_id, circuito_id, es_observado, estado_validacion, es_anulado, timestamp) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
            votos
        )
        print("✓ Votos de ejemplo creados")
        
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