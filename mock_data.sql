-- Script SQL para crear datos mock en la base de datos de votación
-- Ejecutar después de crear las tablas

-- 1. Usuarios de mesa con circuitos asignados (contraseñas hasheadas con bcrypt)
INSERT IGNORE INTO usuarios (username, password_hash, is_active, circuito, role) VALUES
('mesa001', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', true, '001', 'mesa'),
('mesa002', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', true, '002', 'mesa'),
('mesa003', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', true, '003', 'mesa'),
('presidente001', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', true, '001', 'presidente');

-- 2. Partidos políticos uruguayos
INSERT IGNORE INTO partidos (nombre) VALUES
('Frente Amplio'),
('Partido Nacional'),
('Partido Colorado'),
('Cabildo Abierto'),
('Partido Independiente');

-- 3. Candidatos para elecciones generales (1 por partido)
INSERT IGNORE INTO candidatos (nombre, partido_id) VALUES
('Yamandú Orsi', 1),           -- Frente Amplio
('Álvaro Delgado', 2),         -- Partido Nacional  
('Andrés Ojeda', 3),           -- Partido Colorado
('Guido Manini Ríos', 4),     -- Cabildo Abierto
('Pablo Mieres', 5);           -- Partido Independiente

-- 4. Autorizaciones de votantes de ejemplo
INSERT IGNORE INTO autorizaciones (cedula, circuito, estado, autorizado_por, fecha_autorizacion) VALUES
('12345678', '001', 'HABILITADA', 'mesa001', NOW()),
('87654321', '001', 'HABILITADA', 'mesa001', NOW()),
('11111111', '001', 'HABILITADA', 'mesa001', NOW()),
('22222222', '002', 'HABILITADA', 'mesa002', NOW()),
('33333333', '002', 'HABILITADA', 'mesa002', NOW()),
('44444444', '003', 'HABILITADA', 'mesa003', NOW()),
('55555555', '003', 'HABILITADA', 'mesa003', NOW());

-- Verificar datos creados
SELECT 'Usuarios creados:' as info;
SELECT username FROM usuarios;

SELECT 'Partidos creados:' as info;
SELECT nombre FROM partidos;

SELECT 'Candidatos por partido:' as info;
SELECT c.nombre as candidato, p.nombre as partido 
FROM candidatos c 
JOIN partidos p ON c.partido_id = p.id 
ORDER BY p.nombre, c.nombre;

SELECT 'Votantes autorizados:' as info;
SELECT cedula, circuito, estado FROM autorizaciones;