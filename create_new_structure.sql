-- Script para crear la nueva estructura de la base de datos
-- Ejecutar después de hacer backup de la base de datos existente

-- Crear tabla de establecimientos
CREATE TABLE IF NOT EXISTS establecimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    zona VARCHAR(100),
    barrio VARCHAR(100),
    direccion VARCHAR(300) NOT NULL,
    tipo_establecimiento VARCHAR(50) NOT NULL,
    accesible BOOLEAN DEFAULT FALSE,
    INDEX idx_departamento (departamento),
    INDEX idx_ciudad (ciudad)
);

-- Crear tabla de circuitos
CREATE TABLE IF NOT EXISTS circuitos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_circuito VARCHAR(10) NOT NULL UNIQUE,
    establecimiento_id INT,
    FOREIGN KEY (establecimiento_id) REFERENCES establecimientos(id),
    INDEX idx_numero_circuito (numero_circuito)
);

-- Crear tabla de mesas
CREATE TABLE IF NOT EXISTS mesas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_mesa VARCHAR(10) NOT NULL,
    circuito_id INT,
    FOREIGN KEY (circuito_id) REFERENCES circuitos(id),
    INDEX idx_numero_mesa (numero_mesa),
    INDEX idx_circuito_id (circuito_id)
);

-- Insertar datos de ejemplo para testing
INSERT INTO establecimientos (nombre, departamento, ciudad, zona, barrio, direccion, tipo_establecimiento, accesible) VALUES
('Escuela Nacional No. 1', 'Montevideo', 'Montevideo', 'Centro', 'Ciudad Vieja', 'Sarandí 674', 'escuela', TRUE),
('Liceo José Pedro Varela', 'Montevideo', 'Montevideo', 'Centro', 'Cordón', '18 de Julio 1234', 'liceo', TRUE),
('Universidad de la República', 'Montevideo', 'Montevideo', 'Centro', 'Universidad', 'Av. 18 de Julio 1968', 'universidad', TRUE),
('Escuela Rural No. 45', 'Canelones', 'Las Piedras', 'Norte', 'Barrio Nuevo', 'Ruta 5 Km 25', 'escuela', FALSE);

INSERT INTO circuitos (numero_circuito, establecimiento_id) VALUES
('001', 1),
('002', 1),
('003', 2),
('004', 3),
('005', 4);

INSERT INTO mesas (numero_mesa, circuito_id) VALUES
('A1', 1),
('A2', 1),
('B1', 2),
('B2', 2),
('C1', 3),
('C2', 3),
('D1', 4),
('E1', 5);

-- Actualizar tabla usuarios para usar circuito_id en lugar de circuito string
-- NOTA: Primero hacer backup y luego ejecutar estas modificaciones

-- Agregar nueva columna
ALTER TABLE usuarios ADD COLUMN circuito_id INT;

-- Actualizar datos existentes (mapear circuitos string a IDs)
UPDATE usuarios SET circuito_id = 1 WHERE circuito = '001';
UPDATE usuarios SET circuito_id = 2 WHERE circuito = '002';
UPDATE usuarios SET circuito_id = 3 WHERE circuito = '003';
UPDATE usuarios SET circuito_id = 4 WHERE circuito = '004';
UPDATE usuarios SET circuito_id = 5 WHERE circuito = '005';

-- Agregar foreign key
ALTER TABLE usuarios ADD FOREIGN KEY (circuito_id) REFERENCES circuitos(id);

-- Actualizar tabla votos
ALTER TABLE votos ADD COLUMN circuito_id INT;
UPDATE votos v 
JOIN circuitos c ON v.circuito_mesa = c.numero_circuito 
SET v.circuito_id = c.id;
ALTER TABLE votos ADD FOREIGN KEY (circuito_id) REFERENCES circuitos(id);

-- Actualizar tabla autorizaciones
ALTER TABLE autorizaciones ADD COLUMN circuito_id INT;
UPDATE autorizaciones a 
JOIN circuitos c ON a.circuito = c.numero_circuito 
SET a.circuito_id = c.id;
ALTER TABLE autorizaciones ADD FOREIGN KEY (circuito_id) REFERENCES circuitos(id);

-- DESPUÉS DE VERIFICAR QUE TODO FUNCIONA CORRECTAMENTE:
-- Opcional: eliminar columnas viejas
-- ALTER TABLE usuarios DROP COLUMN circuito;
-- ALTER TABLE votos DROP COLUMN circuito_mesa;
-- ALTER TABLE autorizaciones DROP COLUMN circuito;