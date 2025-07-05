#!/usr/bin/env python3
"""
Script para crear las tablas de la base de datos usando SQL directo
"""

from database import get_db_connection

def create_tables():
    """Crear todas las tablas necesarias"""
    
    sql_statements = [
        """
        CREATE TABLE IF NOT EXISTS establecimientos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            departamento VARCHAR(100) NOT NULL,
            ciudad VARCHAR(100) NOT NULL,
            zona VARCHAR(100),
            barrio VARCHAR(100),
            direccion TEXT NOT NULL,
            tipo_establecimiento VARCHAR(100) NOT NULL,
            accesible BOOLEAN DEFAULT FALSE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS circuitos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            numero_circuito VARCHAR(50) NOT NULL UNIQUE,
            numero_mesa VARCHAR(10),
            establecimiento_id INT NOT NULL,
            FOREIGN KEY (establecimiento_id) REFERENCES establecimientos(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            circuito_id INT,
            role VARCHAR(50) DEFAULT 'mesa',
            mesa_cerrada BOOLEAN DEFAULT FALSE,
            fecha_cierre DATETIME,
            FOREIGN KEY (circuito_id) REFERENCES circuitos(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS partidos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL UNIQUE,
            color VARCHAR(7),
            logo_url VARCHAR(500)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS candidatos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            partido_id INT NOT NULL,
            orden_lista INT,
            FOREIGN KEY (partido_id) REFERENCES partidos(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS autorizaciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cedula VARCHAR(20) NOT NULL,
            circuito_id INT NOT NULL,
            estado ENUM('HABILITADA', 'VOTÓ', 'SUSPENDIDA') DEFAULT 'HABILITADA',
            autorizado_por VARCHAR(100),
            fecha_autorizacion DATETIME,
            fecha_voto DATETIME,
            es_autorizacion_especial BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (circuito_id) REFERENCES circuitos(id),
            UNIQUE KEY unique_cedula_auth (cedula)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS votos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cedula VARCHAR(20) NOT NULL UNIQUE,
            candidato_id INT NULL,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            es_observado BOOLEAN DEFAULT FALSE,
            estado_validacion ENUM('pendiente', 'aprobado', 'rechazado') DEFAULT 'aprobado',
            circuito_id INT NOT NULL,
            es_anulado BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (candidato_id) REFERENCES candidatos(id) ON DELETE SET NULL,
            FOREIGN KEY (circuito_id) REFERENCES circuitos(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS credenciales_autorizadas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cedula VARCHAR(20) NOT NULL,
            circuito_id INT NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_cedula_circuito (cedula, circuito_id),
            FOREIGN KEY (circuito_id) REFERENCES circuitos(id) ON DELETE CASCADE
        )
        """
    ]
    
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            
            for sql in sql_statements:
                print(f"Ejecutando: {sql[:50]}...")
                cursor.execute(sql)
            
            connection.commit()
            print("✅ Todas las tablas creadas exitosamente")
            
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")

if __name__ == "__main__":
    create_tables()