import mysql.connector
import os

# Configuración de la base de datos
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'voting_db'
}

def update_database_structure():
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        print("Actualizando estructura de la base de datos...")
        
        # Verificar si las columnas ya existen
        cursor.execute("DESCRIBE usuarios")
        columns = [column[0] for column in cursor.fetchall()]
        
        if 'circuito' not in columns:
            print("Agregando columna 'circuito'...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN circuito VARCHAR(10) NULL")
        else:
            print("Columna 'circuito' ya existe")
            
        if 'role' not in columns:
            print("Agregando columna 'role'...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN role VARCHAR(20) DEFAULT 'mesa'")
        else:
            print("Columna 'role' ya existe")
        
        # Actualizar usuarios existentes si existen
        cursor.execute("SELECT username FROM usuarios")
        existing_users = [row[0] for row in cursor.fetchall()]
        
        if existing_users:
            print("Actualizando usuarios existentes...")
            updates = [
                ("UPDATE usuarios SET circuito = '001', role = 'mesa' WHERE username = 'mesa001'"),
                ("UPDATE usuarios SET circuito = '002', role = 'mesa' WHERE username = 'mesa002'"),
                ("UPDATE usuarios SET circuito = '003', role = 'mesa' WHERE username = 'mesa003'"),
                ("UPDATE usuarios SET circuito = '001', role = 'presidente' WHERE username = 'presidente001'"),
            ]
            
            for update_sql in updates:
                cursor.execute(update_sql)
        
        # Confirmar cambios
        conn.commit()
        print("✅ Base de datos actualizada exitosamente!")
        
        # Mostrar estructura final
        cursor.execute("DESCRIBE usuarios")
        columns = cursor.fetchall()
        print("\n📋 Estructura actual de la tabla usuarios:")
        for column in columns:
            print(f"  - {column[0]} ({column[1]})")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    update_database_structure()