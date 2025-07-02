import mysql.connector
import os

# Configuración de la base de datos
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'voting_db'
}

def update_voto_table():
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        print("Actualizando tabla votos...")
        
        # Verificar si las columnas ya existen
        cursor.execute("DESCRIBE votos")
        columns = [column[0] for column in cursor.fetchall()]
        
        if 'es_observado' not in columns:
            print("Agregando columna 'es_observado'...")
            cursor.execute("ALTER TABLE votos ADD COLUMN es_observado BOOLEAN DEFAULT FALSE")
        else:
            print("Columna 'es_observado' ya existe")
            
        if 'estado_validacion' not in columns:
            print("Agregando columna 'estado_validacion'...")
            cursor.execute("ALTER TABLE votos ADD COLUMN estado_validacion VARCHAR(20) DEFAULT 'aprobado'")
        else:
            print("Columna 'estado_validacion' ya existe")
            
        if 'circuito_mesa' not in columns:
            print("Agregando columna 'circuito_mesa'...")
            cursor.execute("ALTER TABLE votos ADD COLUMN circuito_mesa VARCHAR(10) NULL")
        else:
            print("Columna 'circuito_mesa' ya existe")
        
        # Confirmar cambios
        conn.commit()
        print("✅ Tabla votos actualizada exitosamente!")
        
        # Mostrar estructura final
        cursor.execute("DESCRIBE votos")
        columns = cursor.fetchall()
        print("\n📋 Estructura actual de la tabla votos:")
        for column in columns:
            print(f"  - {column[0]} ({column[1]})")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    update_voto_table()