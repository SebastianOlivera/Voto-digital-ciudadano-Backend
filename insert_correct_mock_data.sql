-- Datos mock con estructura corregida (1:1 circuito-mesa)

-- Establecimientos por departamento
INSERT INTO establecimientos (nombre, departamento, ciudad, zona, barrio, direccion, tipo_establecimiento, accesible) VALUES
-- Montevideo
('Escuela Nacional No. 1', 'Montevideo', 'Montevideo', 'Centro', 'Ciudad Vieja', 'Sarandí 674', 'escuela', TRUE),
('Liceo José Pedro Varela', 'Montevideo', 'Montevideo', 'Centro', 'Cordón', '18 de Julio 1234', 'liceo', TRUE),
('Universidad de la República', 'Montevideo', 'Montevideo', 'Centro', 'Universidad', 'Av. 18 de Julio 1968', 'universidad', TRUE),
('Escuela No. 45', 'Montevideo', 'Montevideo', 'Este', 'Pocitos', 'Av. Brasil 2567', 'escuela', TRUE),

-- Canelones  
('Escuela Rural No. 45', 'Canelones', 'Las Piedras', 'Norte', 'Barrio Nuevo', 'Ruta 5 Km 25', 'escuela', FALSE),
('Liceo de Canelones', 'Canelones', 'Canelones', 'Centro', 'Centro', 'Treinta y Tres 123', 'liceo', TRUE),

-- Maldonado
('Liceo de Punta del Este', 'Maldonado', 'Punta del Este', 'Península', 'Centro', 'Gorlero 456', 'liceo', TRUE),
('Instituto Maldonado', 'Maldonado', 'Maldonado', 'Centro', 'Centro', 'Sarandí 234', 'instituto', FALSE),

-- Colonia
('Escuela de Colonia', 'Colonia', 'Colonia del Sacramento', 'Histórico', 'Barrio Histórico', 'Calle de los Suspiros 12', 'escuela', FALSE),

-- Rocha
('Liceo de Rocha', 'Rocha', 'Rocha', 'Centro', 'Centro', '19 de Abril 678', 'liceo', TRUE);

-- Circuitos con mesas integradas (relación 1:1)
INSERT INTO circuitos (numero_circuito, numero_mesa, establecimiento_id) VALUES
-- Establecimiento 1: 3 circuitos
('001', 'A', 1),
('002', 'B', 1), 
('003', 'C', 1),

-- Establecimiento 2: 2 circuitos
('004', 'A', 2),
('005', 'B', 2),

-- Establecimiento 3: 1 circuito
('006', 'A', 3),

-- Establecimiento 4: 2 circuitos
('007', 'A', 4),
('008', 'B', 4),

-- Establecimiento 5: 2 circuitos 
('016', 'A', 5),
('017', 'B', 5),

-- Establecimiento 6: 1 circuito
('018', 'A', 6),

-- Establecimiento 7: 1 circuito
('026', 'A', 7),

-- Establecimiento 8: 1 circuito
('027', 'A', 8),

-- Establecimiento 9: 1 circuito
('036', 'A', 9),

-- Establecimiento 10: 1 circuito
('041', 'A', 10);

-- Partidos políticos
INSERT IGNORE INTO partidos (nombre) VALUES
('Frente Amplio'),
('Partido Nacional'), 
('Partido Colorado'),
('Cabildo Abierto'),
('Partido Independiente');

-- Candidatos para elecciones generales (1 por partido)
INSERT IGNORE INTO candidatos (nombre, partido_id) VALUES
('Yamandú Orsi', 1),           -- Frente Amplio
('Álvaro Delgado', 2),         -- Partido Nacional  
('Andrés Ojeda', 3),           -- Partido Colorado
('Guido Manini Ríos', 4),     -- Cabildo Abierto
('Pablo Mieres', 5);           -- Partido Independiente

-- Usuarios de mesa (Nota: Usar setup_database.py para hashes correctos)
INSERT INTO usuarios (username, password_hash, circuito_id, role) VALUES
('mesa001', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 1, 'mesa'),
('mesa002', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 2, 'mesa'),
('mesa003', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 3, 'mesa'),
('presidente001', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 1, 'presidente'),
('presidente002', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 2, 'presidente'),
('presidente003', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 3, 'presidente'),
('presidente004', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 4, 'presidente'),
('presidente005', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 5, 'presidente'),
('presidente006', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 6, 'presidente'),
('presidente007', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 7, 'presidente'),
('presidente008', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 8, 'presidente'),
('secretario001', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 1, 'secretario'),
('secretario002', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', 2, 'secretario'),
('admin', '$2b$12$LQv3c1yqBwRXJlvl3n8jI.EzNzNhvj8HqzJ5Q5Q5Q5Q5Q5Q5Q5Q5O', NULL, 'superadmin');

-- Autorizaciones de ejemplo
INSERT INTO autorizaciones (cedula, circuito_id, estado, autorizado_por, es_autorizacion_especial) VALUES
('12345678', 1, 'HABILITADA', 'presidente001', FALSE),
('87654321', 1, 'VOTÓ', 'presidente001', FALSE),
('11111111', 2, 'HABILITADA', 'presidente002', TRUE),
('22222222', 3, 'VOTÓ', 'presidente003', FALSE),
('33333333', 4, 'HABILITADA', 'presidente004', FALSE),
('44444444', 5, 'HABILITADA', 'presidente005', FALSE),
('55555555', 6, 'VOTÓ', 'presidente006', FALSE),
('66666666', 7, 'HABILITADA', 'presidente007', FALSE);

-- Votos de ejemplo
INSERT INTO votos (cedula, candidato_id, circuito_id, es_observado, estado_validacion) VALUES
('87654321', 1, 1, FALSE, 'aprobado'),
('22222222', 2, 3, FALSE, 'aprobado'), 
('55555555', 1, 6, FALSE, 'aprobado'),
('77777777', 3, 1, TRUE, 'pendiente'),
('88888888', 1, 2, FALSE, 'aprobado');