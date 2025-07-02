#!/usr/bin/env python3
"""
Script para ejecutar migraciones de base de datos
"""

import os
import sys
from sqlalchemy import create_engine, text
from database import DATABASE_URL

def run_migration():
    """Ejecuta la migración para agregar la columna es_anulado"""
    try:
        # Crear conexión a la base de datos
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            print("Ejecutando migración: agregar columna es_anulado...")
            
            # Verificar si la columna ya existe
            result = connection.execute(text("""
                SELECT COUNT(*) as count 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'votos' 
                AND COLUMN_NAME = 'es_anulado'
            """))
            
            if result.fetchone()[0] == 0:
                # La columna no existe, agregarla
                connection.execute(text("ALTER TABLE votos ADD COLUMN es_anulado BOOLEAN DEFAULT FALSE"))
                print("✅ Columna es_anulado agregada exitosamente")
                
                # Actualizar registros existentes
                connection.execute(text("UPDATE votos SET es_anulado = FALSE WHERE candidato_id IS NULL"))
                print("✅ Registros existentes actualizados")
                
                connection.commit()
            else:
                print("ℹ️  La columna es_anulado ya existe")
                
    except Exception as e:
        print(f"❌ Error ejecutando migración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()