-- ============================================================
-- ÍNDICES PARA CONSULTAS DO PILOTO
-- ============================================================
-- Os índices auxiliam as consultas do dashboard e dos
-- relatórios do piloto, pois os filtros principais usam driver_id
-- e as junções envolvem race_id, status_id e constructor_id

SET search_path TO projeto_f1;

CREATE INDEX IF NOT EXISTS idx_results_driver_race
ON results(driver_id, race_id);

CREATE INDEX IF NOT EXISTS idx_results_driver_status
ON results(driver_id, status_id);

CREATE INDEX IF NOT EXISTS idx_results_driver_position
ON results(driver_id, position_order);

CREATE INDEX IF NOT EXISTS idx_results_driver_points
ON results(driver_id, points);

CREATE INDEX IF NOT EXISTS idx_results_driver_constructor
ON results(driver_id, constructor_id);

CREATE INDEX IF NOT EXISTS idx_races_circuit_date
ON races(circuit_id, race_date);
