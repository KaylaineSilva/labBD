SET search_path TO projeto_f1;

-- ============================================================
-- Dashboard da escuderia
-- Retorna os dados resumidos da escuderia logada.
-- ============================================================

CREATE OR REPLACE FUNCTION dashboard_escuderia(
    p_constructor_id INTEGER
)
RETURNS TABLE (
    "Escuderia" TEXT,
    "Quantidade de vitórias" BIGINT,
    "Quantidade de pilotos" BIGINT,
    "Primeiro ano" INTEGER,
    "Último ano" INTEGER
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.name::TEXT AS "Escuderia",
        COUNT(*) FILTER (WHERE res.position_order = 1) AS "Quantidade de vitórias",
        COUNT(DISTINCT res.driver_id) AS "Quantidade de pilotos",
        EXTRACT(YEAR FROM MIN(r.race_date))::INTEGER AS "Primeiro ano",
        EXTRACT(YEAR FROM MAX(r.race_date))::INTEGER AS "Último ano"
    FROM constructors c
    LEFT JOIN results res
        ON res.constructor_id = c.id
    LEFT JOIN races r
        ON r.id = res.race_id
    WHERE c.id = p_constructor_id
    GROUP BY c.id, c.name;
END;
$$
LANGUAGE plpgsql;


-- ============================================================
-- Ação: consultar piloto por sobrenome
-- Verifica se o piloto já correu pela escuderia logada.
-- ============================================================

CREATE OR REPLACE FUNCTION consultar_piloto_escuderia_por_sobrenome(
    p_constructor_id INTEGER,
    p_sobrenome TEXT
)
RETURNS TABLE (
    "Nome completo" TEXT,
    "Data de nascimento" DATE,
    "País ou nacionalidade" TEXT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        (d.given_name || ' ' || d.family_name)::TEXT AS "Nome completo",
        d.date_of_birth AS "Data de nascimento",
        COALESCE(co.nationality, co.name, 'Não informado')::TEXT AS "País ou nacionalidade"
    FROM drivers d
    JOIN results res
        ON res.driver_id = d.id
    LEFT JOIN countries co
        ON co.id = d.country_id
    WHERE res.constructor_id = p_constructor_id
      AND LOWER(TRIM(d.family_name)) = LOWER(TRIM(p_sobrenome))
    ORDER BY "Nome completo";
END;
$$
LANGUAGE plpgsql;


-- ============================================================
-- Relatório 4
-- Pilotos da escuderia e quantidade de vitórias.
-- ============================================================

CREATE OR REPLACE FUNCTION relatorio_escuderia_vitorias_pilotos(
    p_constructor_id INTEGER
)
RETURNS TABLE (
    "Piloto" TEXT,
    "Quantidade de vitórias" BIGINT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        (d.given_name || ' ' || d.family_name)::TEXT AS "Piloto",
        COUNT(*) FILTER (WHERE res.position_order = 1) AS "Quantidade de vitórias"
    FROM results res
    JOIN drivers d
        ON d.id = res.driver_id
    WHERE res.constructor_id = p_constructor_id
    GROUP BY
        d.id,
        d.given_name,
        d.family_name
    ORDER BY
        "Quantidade de vitórias" DESC,
        "Piloto";
END;
$$
LANGUAGE plpgsql;


-- ============================================================
-- Relatório 5
-- Quantidade de resultados por status da escuderia logada.
-- ============================================================

CREATE OR REPLACE FUNCTION relatorio_escuderia_status(
    p_constructor_id INTEGER
)
RETURNS TABLE (
    "Status" TEXT,
    "Quantidade de resultados" BIGINT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.status::TEXT AS "Status",
        COUNT(*) AS "Quantidade de resultados"
    FROM results res
    JOIN status s
        ON s.id = res.status_id
    WHERE res.constructor_id = p_constructor_id
    GROUP BY
        s.id,
        s.status
    ORDER BY
        "Quantidade de resultados" DESC;
END;
$$
LANGUAGE plpgsql;