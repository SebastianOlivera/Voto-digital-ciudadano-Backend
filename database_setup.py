import mysql.connector
from passlib.context import CryptContext
from datetime import datetime
import os
import random

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
        
        if 'mesa_cerrada' not in columns:
            print("Agregando columna 'mesa_cerrada'...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN mesa_cerrada BOOLEAN DEFAULT FALSE")
        
        if 'fecha_cierre' not in columns:
            print("Agregando columna 'fecha_cierre'...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN fecha_cierre DATETIME NULL")
        
        # Verificar si las columnas ya existen en votos
        cursor.execute("DESCRIBE votos")
        voto_columns = [column[0] for column in cursor.fetchall()]
        
        if 'es_observado' not in voto_columns:
            print("Agregando columna 'es_observado'...")
            cursor.execute("ALTER TABLE votos ADD COLUMN es_observado BOOLEAN DEFAULT FALSE")
            
        if 'estado_validacion' not in voto_columns:
            print("Agregando columna 'estado_validacion'...")
            cursor.execute("ALTER TABLE votos ADD COLUMN estado_validacion VARCHAR(20) DEFAULT 'aprobado'")
            
        
        # Verificar si las columnas ya existen en autorizaciones
        cursor.execute("DESCRIBE autorizaciones")
        auth_columns = [column[0] for column in cursor.fetchall()]
        
        if 'es_autorizacion_especial' not in auth_columns:
            print("Agregando columna 'es_autorizacion_especial'...")
            cursor.execute("ALTER TABLE autorizaciones ADD COLUMN es_autorizacion_especial BOOLEAN DEFAULT FALSE")
        
        # Crear tablas de elecciones si no existen
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS elecciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            año INT NOT NULL UNIQUE,
            activa BOOLEAN DEFAULT FALSE,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Agregar columnas necesarias a candidatos
        cursor.execute("DESCRIBE candidatos")
        candidato_columns = [column[0] for column in cursor.fetchall()]
        
        if 'es_presidente' not in candidato_columns:
            print("Agregando columna 'es_presidente' a candidatos...")
            cursor.execute("ALTER TABLE candidatos ADD COLUMN es_presidente BOOLEAN DEFAULT TRUE")
            
        if 'numero_lista' not in candidato_columns:
            print("Agregando columna 'numero_lista' a candidatos...")
            cursor.execute("ALTER TABLE candidatos ADD COLUMN numero_lista INT")
            
        if 'eleccion_id' not in candidato_columns:
            print("Agregando columna 'eleccion_id' a candidatos...")
            cursor.execute("ALTER TABLE candidatos ADD COLUMN eleccion_id INT")
            
        # Eliminar logo_url de partidos si existe
        cursor.execute("DESCRIBE partidos")
        partido_columns = [column[0] for column in cursor.fetchall()]
        
        if 'logo_url' in partido_columns:
            print("Eliminando columna 'logo_url' de partidos...")
            cursor.execute("ALTER TABLE partidos DROP COLUMN logo_url")

        # Eliminar columna color de partidos si existe
        if 'color' in partido_columns:
            print("Eliminando columna 'color' de partidos...")
            cursor.execute("ALTER TABLE partidos DROP COLUMN color")
            
        if 'activa' not in partido_columns:
            print("Agregando columna 'activa' a elecciones...")
            cursor.execute("ALTER TABLE elecciones ADD COLUMN activa BOOLEAN DEFAULT FALSE")
        
        
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
        cursor.execute("DELETE FROM elecciones")
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
        
        # 2. Crear circuitos (secuencia completa para testing)
        circuitos = [
            # Montevideo - Establecimientos 1-5
            ('1', 1), ('2', 1), ('3', 1),
            ('4', 2), ('5', 2), ('6', 2),
            ('7', 3), ('8', 3), ('9', 3),
            ('10', 4), ('11', 4), ('12', 4),
            ('13', 5), ('14', 5), ('15', 5),
            # Canelones - Establecimientos 6-9
            ('16', 6), ('17', 6), ('18', 7),
            ('19', 8), ('20', 9),
            # Maldonado - Establecimientos 10-12
            ('21', 10), ('22', 11), ('23', 12),
            # Colonia - Establecimientos 13-14
            ('24', 13), ('25', 14),
            # Rocha - Establecimientos 15-16
            ('26', 15), ('27', 16),
            # Rivera - Establecimientos 17-18
            ('28', 17), ('29', 18),
            # Salto - Establecimientos 19-20
            ('30', 19), ('31', 20),
            # Paysandú - Establecimientos 21-22
            ('32', 21), ('33', 22),
            # Soriano - Establecimiento 23
            ('34', 23),
            # Tacuarembó - Establecimiento 24
            ('35', 24),
        ]
        
        cursor.executemany(
            "INSERT INTO circuitos (numero_circuito, establecimiento_id) VALUES (%s, %s)",
            circuitos
        )
        print("✓ Circuitos creados")
        
        # Clear credenciales_autorizadas and add some examples
        cursor.execute("DELETE FROM credenciales_autorizadas")
        print("✓ Tabla credenciales_autorizadas limpiada")
        
        # Agregar credenciales específicas por circuito
        credenciales_por_circuito = [
            # Circuito 1
            ('ABC1001', 1), ('ABC1002', 1), ('ABC1003', 1), ('ABC1004', 1), ('ABC1005', 1),
            # Circuito 2
            ('ABC2001', 2), ('ABC2002', 2), ('ABC2003', 2), ('ABC2004', 2), ('ABC2005', 2),
            # Circuito 3
            ('ABC3001', 3), ('ABC3002', 3), ('ABC3003', 3), ('ABC3004', 3), ('ABC3005', 3),
        ]
        
        cursor.executemany(
            "INSERT INTO credenciales_autorizadas (credencial, circuito_id) VALUES (%s, %s)",
            credenciales_por_circuito
        )
        print("✓ Credenciales específicas por circuito creadas")
        
        # 3. Crear partidos
        partidos_data = [
            ('Frente Amplio',),
            ('Partido Nacional',),
            ('Partido Colorado',),
            ('Cabildo Abierto',),
            ('Partido Independiente',)
        ]
        cursor.executemany("INSERT INTO partidos (nombre) VALUES (%s)", partidos_data)
        print("✓ Partidos creados")
        
        # 4. Crear elección activa
        cursor.execute("INSERT INTO elecciones (año, activa) VALUES (2024, TRUE)")
        eleccion_id = cursor.lastrowid
        print("✓ Elección 2024 creada y marcada como activa")
        
        # 5. Crear candidatos para la elección
        candidatos_data = [
            ('Juan Pérez', 1, True, 501, eleccion_id),     # Frente Amplio
            ('María González', 2, True, 15, eleccion_id),   # Partido Nacional  
            ('Carlos López', 3, True, 25, eleccion_id),     # Partido Colorado
            ('Ana Rodríguez', 4, True, 71, eleccion_id),   # Cabildo Abierto
            ('Luis Martínez', 5, True, 77, eleccion_id),   # Partido Independiente
        ]
        
        cursor.executemany(
            "INSERT INTO candidatos (nombre, partido_id, es_presidente, numero_lista, eleccion_id) VALUES (%s, %s, %s, %s, %s)",
            candidatos_data
        )
        print("✓ Candidatos presidenciales creados")
        
        # 6. Crear usuarios mock (solo mesa y presidente)
        password_hash = pwd_context.hash("password123")
        usuarios = [
            ("mesa1", password_hash, True, 1, "mesa"),
            ("mesa2", password_hash, True, 2, "mesa"),
            ("mesa3", password_hash, True, 3, "mesa"),
            ("presidente1", password_hash, True, 1, "presidente"),
            ("presidente2", password_hash, True, 2, "presidente"),
            ("presidente3", password_hash, True, 3, "presidente"),
        ]
        
        cursor.executemany(
            "INSERT INTO usuarios (username, password_hash, is_active, circuito_id, role) VALUES (%s, %s, %s, %s, %s)",
            usuarios
        )
        print("✓ Usuarios mock creados (mesa y presidente)")
        
        # 7. Generar votos con distribución realista para la elección
        votos = []
        
        # Contadores por circuito para generar comprobantes únicos
        circuito_counters = {}
        
        # Generar 500 votos de ejemplo con distribución realista
        for i in range(500):
            # 50% votos a candidatos, 30% en blanco, 20% anulados
            rand = random.random()
            if rand < 0.5:
                # Voto a candidato (IDs 1-5 que creamos)
                candidato_id = random.randint(1, 5)
                es_anulado = False
            elif rand < 0.8:
                candidato_id = None  # Voto en blanco (NULL)
                es_anulado = False
            else:
                candidato_id = None
                es_anulado = True  # Voto anulado
                
            # Debug: Mostrar que circuito se está generando
            circuito_id = random.randint(1, 35)
            if i < 10:  # Solo los primeros 10 para debug
                print(f"DEBUG: Generando voto {i+1} para circuito_id={circuito_id}")
            es_observado = random.random() < 0.05  # 5% de votos observados
            
            # Generar comprobante único para el circuito
            if circuito_id not in circuito_counters:
                circuito_counters[circuito_id] = 1
            else:
                circuito_counters[circuito_id] += 1
            
            numero_comprobante = f"C{circuito_id:03d}-{circuito_counters[circuito_id]:05d}"
            votos.append((numero_comprobante, candidato_id, circuito_id, es_observado, 'aprobado', es_anulado))
        
        cursor.executemany(
            "INSERT INTO votos (numero_comprobante, candidato_id, circuito_id, es_observado, estado_validacion, es_anulado, timestamp) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
            votos
        )
        print("✓ Votos de ejemplo creados (con distribución realista)")
        
        # Debug: Verificar votos por circuito
        cursor.execute("""
            SELECT c.numero_circuito, COUNT(v.id) as total_votos
            FROM circuitos c
            LEFT JOIN votos v ON c.id = v.circuito_id
            GROUP BY c.id, c.numero_circuito
            ORDER BY CAST(c.numero_circuito AS UNSIGNED)
            LIMIT 15
        """)
        votos_por_circuito = cursor.fetchall()
        print(f"🔍 DEBUG: Votos por circuito (primeros 15): {votos_por_circuito}")
        
        print("\n🎯 ELECCIÓN 2024 CREADA:")
        print("   - Elección activa con 5 candidatos presidenciales")
        print("   - 500 votos distribuidos en TODOS los circuitos (1-35)")
        print("   - Al crear una nueva elección, los votos se limpiarán automáticamente")
        
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
        print("Usuario: presidente1, Contraseña: password123")
        print("ℹ️  Para crear usuario admin ejecuta: python create_admin_user.py")
        
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
        
        if 'mesa_cerrada' not in columns:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN mesa_cerrada BOOLEAN DEFAULT FALSE")
        
        if 'fecha_cierre' not in columns:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN fecha_cierre DATETIME NULL")
        
        # Verificar si las columnas ya existen en votos
        cursor.execute("DESCRIBE votos")
        voto_columns = [column[0] for column in cursor.fetchall()]
        
        if 'es_observado' not in voto_columns:
            cursor.execute("ALTER TABLE votos ADD COLUMN es_observado BOOLEAN DEFAULT FALSE")
            
        if 'estado_validacion' not in voto_columns:
            cursor.execute("ALTER TABLE votos ADD COLUMN estado_validacion VARCHAR(20) DEFAULT 'aprobado'")
            
        
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
        print("Usuario: presidente1, Contraseña: password123")
        print("ℹ️  Para crear usuario admin ejecuta: python create_admin_user.py")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()