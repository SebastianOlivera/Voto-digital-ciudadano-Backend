-- Script para actualizar la tabla usuarios con las nuevas columnas
-- Ejecutar este script ANTES de crear los datos mock

USE voting_db;

-- Agregar las nuevas columnas a la tabla usuarios
ALTER TABLE usuarios 
ADD COLUMN circuito VARCHAR(10) NULL,
ADD COLUMN role VARCHAR(20) DEFAULT 'mesa';

-- Actualizar los usuarios existentes con circuitos por defecto
UPDATE usuarios SET circuito = '001', role = 'mesa' WHERE username = 'mesa001';
UPDATE usuarios SET circuito = '002', role = 'mesa' WHERE username = 'mesa002';
UPDATE usuarios SET circuito = '003', role = 'mesa' WHERE username = 'mesa003';
UPDATE usuarios SET circuito = '001', role = 'presidente' WHERE username = 'presidente001';

-- Agregar la nueva columna para votos observados
ALTER TABLE autorizaciones 
ADD COLUMN es_autorizacion_especial BOOLEAN DEFAULT FALSE;

-- Verificar la estructura actualizada
DESCRIBE usuarios;
DESCRIBE autorizaciones;