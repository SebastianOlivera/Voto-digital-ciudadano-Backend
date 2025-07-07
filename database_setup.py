from dotenv import load_dotenv
from passlib.context import CryptContext
from database import get_db_connection  # Importas tu pool
import random

load_dotenv()

# Para generar hashes de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_mock_data():
    with get_db_connection() as connection:
        cursor = connection.cursor()
        
        # 1. Crear establecimientos
        establecimientos = [
            ('Escuela Nacional No. 1', 'Montevideo', 'Montevideo', 'Centro', 'Ciudad Vieja', 'Sarandí 674', 'escuela', True),
            ('Liceo José Pedro Varela', 'Montevideo', 'Montevideo', 'Centro', 'Cordón', '18 de Julio 1234', 'liceo', True),
            # (Agrega el resto si querés)
        ]
        cursor.executemany(
            """
            INSERT INTO establecimientos (
                nombre, departamento, ciudad, zona, barrio, direccion, tipo_establecimiento, accesible
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            establecimientos
        )
        print("✓ Establecimientos creados")
        
        # 2. Crear circuitos
        circuitos = [
            ('1', 1), ('2', 1), ('3', 1),
            ('4', 2), ('5', 2)
        ]
        cursor.executemany(
            "INSERT INTO circuitos (numero_circuito, establecimiento_id) VALUES (%s, %s)",
            circuitos
        )
        print("✓ Circuitos creados")
        
        # 3. Crear partidos
        partidos_data = [
            ('Frente Amplio',),
            ('Partido Nacional',),
            ('Partido Colorado',)
        ]
        cursor.executemany(
            "INSERT INTO partidos (nombre) VALUES (%s)",
            partidos_data
        )
        print("✓ Partidos creados")
        
        # 4. Crear elección activa
        cursor.execute("INSERT INTO elecciones (año, activa) VALUES (2024, TRUE)")
        eleccion_id = cursor.lastrowid
        print("✓ Elección 2024 creada y marcada como activa")
        
        # 5. Crear candidatos
        candidatos_data = [
            ('Juan Pérez', 1, True, 501, eleccion_id),
            ('María González', 2, True, 15, eleccion_id),
            ('Carlos López', 3, True, 25, eleccion_id)
        ]
        cursor.executemany(
            """
            INSERT INTO candidatos (
                nombre, partido_id, es_presidente, numero_lista, eleccion_id
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            candidatos_data
        )
        print("✓ Candidatos creados")
        
        # 6. Crear usuarios
        password_hash = pwd_context.hash("password123")
        usuarios = [
            ("mesa1", password_hash, True, 1, "mesa"),
            ("presidente1", password_hash, True, 1, "presidente")
        ]
        cursor.executemany(
            """
            INSERT INTO usuarios (
                username, password_hash, is_active, circuito_id, role
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            usuarios
        )
        print("✓ Usuarios mock creados")
        
        # 7. Crear votos
        votos = []
        circuito_counters = {}
        for i in range(50):
            rand = random.random()
            if rand < 0.5:
                candidato_id = random.randint(1, 3)
                es_anulado = False
            elif rand < 0.8:
                candidato_id = None
                es_anulado = False
            else:
                candidato_id = None
                es_anulado = True
            
            circuito_id = random.randint(1, 3)
            circuito_counters[circuito_id] = circuito_counters.get(circuito_id, 0) + 1
            numero_comprobante = f"C{circuito_id:03d}-{circuito_counters[circuito_id]:05d}"
            votos.append((
                numero_comprobante, candidato_id, circuito_id, False, 'aprobado', es_anulado
            ))
        
        cursor.executemany(
            """
            INSERT INTO votos (
                numero_comprobante, candidato_id, circuito_id,
                es_observado, estado_validacion, es_anulado, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            votos
        )
        print("✓ Votos creados")
        
        connection.commit()
        print("🎉 Datos mock creados exitosamente!")

def main():
    print("=== CREADOR DE DATOS MOCK ===")
    create_mock_data()
    print("Proceso completo.")

if __name__ == "__main__":
    main()
