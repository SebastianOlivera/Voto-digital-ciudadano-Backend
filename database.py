from dotenv import load_dotenv
import mysql.connector.pooling
import os
from contextlib import contextmanager
from typing import Generator
load_dotenv()

# Configuración del pool de conexiones
POOL_CONFIG = {
    'pool_name': 'voting_pool',
    'pool_size': 10,
    'pool_reset_session': True,
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'user'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'voting_db'),
    'charset': 'utf8mb4',
    'autocommit': False
}

# Pool global de conexiones
_connection_pool = None

def init_connection_pool():
    """Inicializar el pool de conexiones"""
    global _connection_pool
    if _connection_pool is None:
        # mostrar configuración
        print(f"DB_HOST: {os.getenv('DB_HOST', 'localhost')}")
        print(f"DB_PORT: {os.getenv('DB_PORT', '3306')}")
        print(f"DB_USER: {os.getenv('DB_USER', 'user')}")
        print(f"DB_NAME: {os.getenv('DB_NAME', 'voting_db')}")
        print(f"Pool config: {POOL_CONFIG}")
        _connection_pool = mysql.connector.pooling.MySQLConnectionPool(**POOL_CONFIG)
    return _connection_pool

def get_connection():
    """Obtener una conexión del pool"""
    if _connection_pool is None:
        init_connection_pool()
    return _connection_pool.get_connection()

@contextmanager
def get_db_connection() -> Generator[mysql.connector.MySQLConnection, None, None]:
    """Context manager para manejar conexiones automáticamente"""
    connection = None
    try:
        connection = get_connection()
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()

@contextmanager
def get_db_transaction() -> Generator[mysql.connector.MySQLConnection, None, None]:
    """Context manager para manejar transacciones automáticamente"""
    connection = None
    try:
        connection = get_connection()
        yield connection
        connection.commit()
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()