-- Migración para agregar la columna es_anulado a la tabla votos
ALTER TABLE votos ADD COLUMN es_anulado BOOLEAN DEFAULT FALSE;

-- Actualizar votos existentes que son anulados (asumiendo que candidato_id = -1 significa anulado)
-- Como no hay votos con candidato_id = -1 aún, todos los votos con candidato_id = NULL son votos en blanco
UPDATE votos SET es_anulado = FALSE WHERE candidato_id IS NULL;