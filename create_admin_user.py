import mysql.connector
from passlib.context import CryptContext
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

def create_admin_user():
    """Crear usuario administrador del sistema"""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        print("Creando usuario administrador del sistema...")
        
        # Verificar si ya existe el usuario admin
        cursor.execute("SELECT username FROM usuarios WHERE username = 'admin'")
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            print("⚠️  Usuario admin ya existe, actualizando contraseña...")
            password_hash = pwd_context.hash("admin123")
            cursor.execute("""
                UPDATE usuarios 
                SET password_hash = %s, is_active = TRUE, role = 'superadmin', circuito_id = NULL
                WHERE username = 'admin'
            """, (password_hash,))
        else:
            print("✓ Creando nuevo usuario admin...")
            password_hash = pwd_context.hash("admin123")
            # Admin no necesita circuito específico, usar NULL
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