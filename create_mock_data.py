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

def create_mock_data():
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        print("Creando datos mock...")
        
        # 1. Usuarios de mesa con circuitos asignados
        usuarios_mesa = [
            ("mesa001", pwd_context.hash("password123"), True, "001", "mesa"),
            ("mesa002", pwd_context.hash("password123"), True, "002", "mesa"),
            ("mesa003", pwd_context.hash("password123"), True, "003", "mesa"),
            ("presidente001", pwd_context.hash("admin123"), True, "001", "presidente"),
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO usuarios (username, password_hash, is_active, circuito, role) VALUES (%s, %s, %s, %s, %s)",
            usuarios_mesa
        )
        print("✓ Usuarios de mesa creados")
        
        # 2. Partidos políticos
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
        
        # 3. Candidatos para elecciones generales (1 por partido)
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
        
        # 4. Autorizaciones de ejemplo (votantes habilitados)
        autorizaciones = [
            ("12345678", "001", "HABILITADA", "mesa001", datetime.now(), None),
            ("87654321", "001", "HABILITADA", "mesa001", datetime.now(), None),
            ("11111111", "001", "HABILITADA", "mesa001", datetime.now(), None),
            ("22222222", "002", "HABILITADA", "mesa002", datetime.now(), None),
            ("33333333", "002", "HABILITADA", "mesa002", datetime.now(), None),
            ("44444444", "003", "HABILITADA", "mesa003", datetime.now(), None),
            ("55555555", "003", "HABILITADA", "mesa003", datetime.now(), None),
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO autorizaciones (cedula, circuito, estado, autorizado_por, fecha_autorizacion, fecha_voto) VALUES (%s, %s, %s, %s, %s, %s)",
            autorizaciones
        )
        print("✓ Autorizaciones de votantes creadas")
        
        # Confirmar cambios
        conn.commit()
        print("\n🎉 Datos mock creados exitosamente!")
        print("\n📋 Datos creados:")
        print("- 4 usuarios de mesa (mesa001, mesa002, mesa003, presidente001)")
        print("- 5 partidos políticos uruguayos")
        print("- 5 candidatos (1 por partido para elecciones generales)")
        print("- 7 votantes autorizados en diferentes circuitos")
        print("\n🔑 Credenciales de prueba:")
        print("Usuario: mesa001, Contraseña: password123")
        print("Usuario: presidente001, Contraseña: admin123")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_mock_data()