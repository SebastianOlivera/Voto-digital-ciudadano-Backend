from dotenv import load_dotenv
from passlib.context import CryptContext
from database import get_db_connection  # Usás tu pool
import os

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    with get_db_connection() as connection:
        cursor = connection.cursor()

        print("Creando usuario administrador del sistema...")

        # Verificar si ya existe el usuario admin
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

        connection.commit()
        print("Usuario administrador creado")
        print("Usuario: admin")
        print("Contraseña: admin123")

if __name__ == "__main__":
    create_admin_user()
