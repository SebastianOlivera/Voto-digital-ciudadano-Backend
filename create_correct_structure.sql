-- Nueva estructura con relación 1:1 entre circuito y mesa

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

-- Crear tabla de circuitos (con mesa integrada 1:1)
CREATE TABLE IF NOT EXISTS circuitos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_circuito VARCHAR(10) NOT NULL UNIQUE,
    numero_mesa VARCHAR(10) NOT NULL,
    establecimiento_id INT,
    FOREIGN KEY (establecimiento_id) REFERENCES establecimientos(id),
    INDEX idx_numero_circuito (numero_circuito),
    INDEX idx_numero_mesa (numero_mesa)
);

-- Eliminar tabla mesas (ya no necesaria)
DROP TABLE IF EXISTS mesas;