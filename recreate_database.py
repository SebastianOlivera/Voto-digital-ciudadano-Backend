#!/usr/bin/env python3
"""
Script para recrear completamente la base de datos con la estructura actualizada
"""

import os
from sqlalchemy import create_engine, text
from database import DATABASE_URL, Base
import models

def recreate_database():
    """Elimina y recrea todas las tablas con la estructura actualizada"""
    try:
        # Crear conexión a la base de datos
        engine = create_engine(DATABASE_URL)
        
        print("🗑️  Eliminando todas las tablas...")
        Base.metadata.drop_all(bind=engine)
        
        print("🔨 Creando tablas con estructura actualizada...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Base de datos recreada exitosamente")
        print("ℹ️  Ahora puedes ejecutar setup_database.py para insertar los datos de prueba")
        
    except Exception as e:
        print(f"❌ Error recreando base de datos: {e}")

if __name__ == "__main__":
    recreate_database()