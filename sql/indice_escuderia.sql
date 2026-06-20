SET search_path TO projeto_f1;

-- ============================================================
-- Índices para consultas da Escuderia
-- ============================================================

-- Ajuda dashboard e relatório 4:
-- filtro por constructor_id, agrupamento por driver_id e contagem de vitórias.
CREATE INDEX IF NOT EXISTS idx_results_constructor_driver_position
ON results(constructor_id, driver_id, position_order);

-- Ajuda relatório 5:
-- filtro por constructor_id e agrupamento por status_id.
CREATE INDEX IF NOT EXISTS idx_results_constructor_status
ON results(constructor_id, status_id);

-- Ajuda dashboard:
-- filtro por constructor_id e junção com races via race_id.
CREATE INDEX IF NOT EXISTS idx_results_constructor_race
ON results(constructor_id, race_id);

-- Ajuda a ação de consultar piloto por sobrenome.
CREATE INDEX IF NOT EXISTS idx_drivers_family_name_normalizado
ON drivers (LOWER(TRIM(family_name)));

-- Ajuda a validação de duplicidade no upload de pilotos.
CREATE INDEX IF NOT EXISTS idx_drivers_nome_completo_normalizado
ON drivers (
    LOWER(TRIM(given_name)),
    LOWER(TRIM(family_name))
);