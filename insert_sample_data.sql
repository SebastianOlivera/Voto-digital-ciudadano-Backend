-- Datos mock con estructura corregida (1:1 circuito-mesa)

-- Establecimientos por departamento
INSERT INTO establecimientos (nombre, departamento, ciudad, zona, barrio, direccion, tipo_establecimiento, accesible) VALUES
-- Montevideo
('Escuela Nacional No. 1', 'Montevideo', 'Montevideo', 'Centro', 'Ciudad Vieja', 'Sarandí 674', 'escuela', TRUE),
('Liceo José Pedro Varela', 'Montevideo', 'Montevideo', 'Centro', 'Cordón', '18 de Julio 1234', 'liceo', TRUE),
('Universidad de la República', 'Montevideo', 'Montevideo', 'Centro', 'Universidad', 'Av. 18 de Julio 1968', 'universidad', TRUE),
('Escuela No. 45', 'Montevideo', 'Montevideo', 'Este', 'Pocitos', 'Av. Brasil 2567', 'escuela', TRUE),
('Escuela Artigas', 'Montevideo', 'Montevideo', 'Oeste', 'Cerro', 'Carlos María Ramírez 1456', 'escuela', TRUE),

-- Canelones  
('Escuela Rural No. 45', 'Canelones', 'Las Piedras', 'Norte', 'Barrio Nuevo', 'Ruta 5 Km 25', 'escuela', FALSE),
('Liceo de Canelones', 'Canelones', 'Canelones', 'Centro', 'Centro', 'Treinta y Tres 123', 'liceo', TRUE),
('Escuela de Pando', 'Canelones', 'Pando', 'Este', 'Centro', 'Leandro Gómez 789', 'escuela', TRUE),
('Instituto Santa Lucía', 'Canelones', 'Santa Lucía', 'Sur', 'Centro', 'José Batlle y Ordóñez 456', 'instituto', TRUE),

-- Maldonado
('Liceo de Punta del Este', 'Maldonado', 'Punta del Este', 'Península', 'Centro', 'Gorlero 456', 'liceo', TRUE),
('Instituto Maldonado', 'Maldonado', 'Maldonado', 'Centro', 'Centro', 'Sarandí 234', 'instituto', FALSE),
('Escuela de San Carlos', 'Maldonado', 'San Carlos', 'Norte', 'Centro', 'Artigas 345', 'escuela', TRUE),

-- Colonia
('Escuela de Colonia', 'Colonia', 'Colonia del Sacramento', 'Histórico', 'Barrio Histórico', 'Calle de los Suspiros 12', 'escuela', FALSE),
('Liceo de Rosario', 'Colonia', 'Rosario', 'Centro', 'Centro', 'General Artigas 567', 'liceo', TRUE),

-- Rocha
('Liceo de Rocha', 'Rocha', 'Rocha', 'Centro', 'Centro', '19 de Abril 678', 'liceo', TRUE),
('Escuela de Chuy', 'Rocha', 'Chuy', 'Frontera', 'Centro', 'Av. Brasil 890', 'escuela', FALSE),

-- Rivera
('Liceo Departamental Rivera', 'Rivera', 'Rivera', 'Centro', 'Centro', 'Sarandí 123', 'liceo', TRUE),
('Escuela de Tranqueras', 'Rivera', 'Tranqueras', 'Rural', 'Centro', 'Ruta 5 Km 463', 'escuela', FALSE),

-- Salto
('Liceo José Pedro Varela', 'Salto', 'Salto', 'Centro', 'Centro', 'Uruguay 456', 'liceo', TRUE),
('Escuela de Constitución', 'Salto', 'Constitución', 'Norte', 'Centro', 'Artigas 789', 'escuela', TRUE),

-- Paysandú
('Liceo No. 1 Paysandú', 'Paysandú', 'Paysandú', 'Centro', 'Centro', '18 de Julio 234', 'liceo', TRUE),
('Escuela de Guichón', 'Paysandú', 'Guichón', 'Este', 'Centro', 'General Flores 567', 'escuela', FALSE),

-- Soriano
('Liceo de Mercedes', 'Soriano', 'Mercedes', 'Centro', 'Centro', 'Giménez 345', 'liceo', TRUE),

-- Tacuarembó
('Liceo de Tacuarembó', 'Tacuarembó', 'Tacuarembó', 'Centro', 'Centro', 'Wilson Ferreira 678', 'liceo', TRUE);

-- Circuitos con mesas integradas (relación 1:1)
INSERT INTO circuitos (numero_circuito, numero_mesa, establecimiento_id) VALUES
-- Montevideo (establecimientos 1-5)
('001', 'A', 1), ('002', 'B', 1), ('003', 'C', 1),
('004', 'A', 2), ('005', 'B', 2),
('006', 'A', 3),
('007', 'A', 4), ('008', 'B', 4),
('009', 'A', 5),

-- Canelones (establecimientos 6-9)  
('016', 'A', 6), ('017', 'B', 6),
('018', 'A', 7),
('019', 'A', 8),
('020', 'A', 9),

-- Maldonado (establecimientos 10-12)
('026', 'A', 10),
('027', 'A', 11),
('028', 'A', 12),

-- Colonia (establecimientos 13-14)
('036', 'A', 13),
('037', 'A', 14),

-- Rocha (establecimientos 15-16)
('041', 'A', 15),
('042', 'A', 16),

-- Rivera (establecimientos 17-18)
('051', 'A', 17),
('052', 'A', 18),

-- Salto (establecimientos 19-20)
('061', 'A', 19),
('062', 'A', 20),

-- Paysandú (establecimientos 21-22)
('071', 'A', 21),
('072', 'A', 22),

-- Soriano (establecimiento 23)
('081', 'A', 23),

-- Tacuarembó (establecimiento 24)
('091', 'A', 24);

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

-- Votos de ejemplo distribuidos por departamentos
INSERT INTO votos (cedula, candidato_id, circuito_id, es_observado, estado_validacion) VALUES
-- Montevideo
('87654321', 1, 1, FALSE, 'aprobado'),
('77777777', 3, 1, TRUE, 'pendiente'),
('88888888', 1, 2, FALSE, 'aprobado'),
('12341234', 2, 3, FALSE, 'aprobado'),
('56785678', 1, 4, FALSE, 'aprobado'),
('91029103', 4, 5, FALSE, 'aprobado'),
('34563456', 2, 6, FALSE, 'aprobado'),
('78907890', 3, 7, FALSE, 'aprobado'),
('23452345', 1, 8, FALSE, 'aprobado'),
('67896789', 5, 9, FALSE, 'aprobado'),

-- Canelones 
('22222222', 2, 16, FALSE, 'aprobado'),
('11112222', 1, 17, FALSE, 'aprobado'),
('33334444', 3, 18, FALSE, 'aprobado'),
('55556666', 2, 19, FALSE, 'aprobado'),
('77778888', 1, 20, FALSE, 'aprobado'),

-- Maldonado
('55555555', 1, 26, FALSE, 'aprobado'),
('44445555', 2, 27, FALSE, 'aprobado'),
('66667777', 3, 28, FALSE, 'aprobado'),

-- Colonia
('33333333', 4, 36, FALSE, 'aprobado'),
('22223333', 1, 37, FALSE, 'aprobado'),

-- Rocha
('66666666', 2, 41, FALSE, 'aprobado'),
('55556666', 1, 42, FALSE, 'aprobado'),

-- Rivera
('11111111', 3, 51, FALSE, 'aprobado'),
('99990000', 2, 52, FALSE, 'aprobado'),

-- Salto
('88889999', 1, 61, FALSE, 'aprobado'),
('77778888', 4, 62, FALSE, 'aprobado'),

-- Paysandú
('66667777', 2, 71, FALSE, 'aprobado'),
('55554444', 1, 72, FALSE, 'aprobado'),

-- Soriano
('44443333', 3, 81, FALSE, 'aprobado'),

-- Tacuarembó
('33332222', 1, 91, FALSE, 'aprobado');