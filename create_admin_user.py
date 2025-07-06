import mysql.connector
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
load_dotenv()

# Configuración de la base de datos
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'defecto'),
    'port': int(os.getenv('DB_PORT', 'defecto')),
    'user': os.getenv('DB_USER', 'defecto'),
    'password': os.getenv('DB_PASSWORD', 'defecto'),
    'database': os.getenv('DB_NAME', 'defecto')
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        print("Creando usuario administrador del sistema...")

        cursor.execute("SELECT username FROM usuarios WHERE username = 'admin'")
        existing_admin = cursor.fetchone()

        password_hash = pwd_context.hash("admin123")

        if existing_admin:
            print("⚠️  Usuario admin ya existe, actualizando contraseña...")
            cursor.execute("""
                UPDATE usuarios 
                SET password_hash = %s, is_active = TRUE, role = 'superadmin', circuito_id = NULL
                WHERE username = 'admin'
            """, (password_hash,))
        else:
            print("✓ Creando nuevo usuario admin...")
            cursor.execute("""
                INSERT INTO usuarios (username, password_hash, is_active, circuito_id, role) 
                VALUES (%s, %s, %s, NULL, %s)
            """, ("admin", password_hash, True, "superadmin"))

        conn.commit()
        print("✅ Usuario administrador creado/actualizado exitosamente!")
        print("\n🔑 Credenciales del administrador:")
        print("Usuario: admin")
        print("Contraseña: admin123")
        print("Rol: superadmin")

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_admin_user()
