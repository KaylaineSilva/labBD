SET search_path TO projeto_f1;

DROP VIEW IF EXISTS vw_piloto_periodo_base CASCADE;
DROP VIEW IF EXISTS vw_piloto_resultados_completos CASCADE;

-- ============================================================
-- VISÃO 1: Resultados completos dos pilotos
-- ============================================================
-- Esta visão centraliza as junções entre pilotos, resultados
-- corridas, circuitos, escuderias e status
-- Ela é usada como base para o dashboard e para os relatórios
-- do usuário do tipo Piloto

CREATE OR REPLACE VIEW vw_piloto_resultados_completos AS
SELECT
    d.id AS driver_id,
    d.driver_ref,
    (d.given_name || ' ' || d.family_name)::TEXT AS nome_piloto,

    r.race_id,
    r.constructor_id,
    r.status_id,
    r.points,
    r.position_order,

    ra.race_name::TEXT AS corrida,
    ra.race_date,
    EXTRACT(YEAR FROM ra.race_date)::INTEGER AS ano,

    ci.id AS circuit_id,
    ci.name::TEXT AS circuito,

    c.name::TEXT AS escuderia,

    st.status::TEXT AS status
FROM drivers d
JOIN results r ON r.driver_id = d.id
JOIN races ra ON ra.id = r.race_id
JOIN circuits ci ON ci.id = ra.circuit_id
JOIN constructors c ON c.id = r.constructor_id
JOIN status st ON st.id = r.status_id;


-- ============================================================
-- VISÃO 2: Período do piloto na base
-- ============================================================
-- Esta visão calcula, para cada piloto, o primeiro e o último
-- ano em que há registros na tabela results

CREATE OR REPLACE VIEW vw_piloto_periodo_base AS
SELECT
    driver_id,
    nome_piloto,
    MIN(ano)::INTEGER AS primeiro_ano,
    MAX(ano)::INTEGER AS ultimo_ano
FROM vw_piloto_resultados_completos
GROUP BY driver_id, nome_piloto;

