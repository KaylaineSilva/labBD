
SET search_path TO projeto_f1;

-- ============================================================
-- Aeroportos próximos de uma cidade brasileira
-- ============================================================

CREATE OR REPLACE FUNCTION buscar_aeroportos_proximos_brasil(
    p_cidade_busca TEXT 
)
RETURNS TABLE (
    "Cidade pesquisada" TEXT,
    "Código IATA" TEXT,
    "Nome do aeroporto" TEXT,
    "Cidade do aeroporto" TEXT,
    "Distância em km" NUMERIC,
    "Tipo do aeroporto" TEXT
)
AS $$
BEGIN
    RETURN QUERY
    WITH cidades_pesquisadas AS (
        SELECT
            ci.id,
            ci.name AS cidade_pesquisada,
            ci.latitude AS latitude_cidade,
            ci.longitude AS longitude_cidade
        FROM cities ci
        JOIN countries co
            ON co.id = ci.country_id
        WHERE 
            TRANSLATE( 
                LOWER(TRIM(ci.name)),
                'áàãâäéèêëíìîïóòõôöúùûüç',
                'aaaaaeeeeiiiiooooouuuuc'
            )
            =
            TRANSLATE(
                LOWER(TRIM(p_cidade_busca)),
                'áàãâäéèêëíìîïóòõôöúùûüç',
                'aaaaaeeeeiiiiooooouuuuc'
            )
            AND co.code = 'BR'
            AND ci.latitude IS NOT NULL
            AND ci.longitude IS NOT NULL
    ),

    aeroportos_brasileiros AS (
        SELECT
            a.id,
            a.name AS nome_aeroporto,
            a.iata_code,
            a.latitude_deg,
            a.longitude_deg,
            cidade_aeroporto.name AS cidade_aeroporto,
            tipo.type AS tipo_aeroporto
        FROM airports a
        JOIN cities cidade_aeroporto
            ON cidade_aeroporto.id = a.city_id
        JOIN countries co
            ON co.id = cidade_aeroporto.country_id
        JOIN airport_types tipo
            ON tipo.id = a.airport_type_id
        WHERE (
            co.code = 'BR'
        )
        AND tipo.type IN ('medium_airport', 'large_airport')
        AND a.latitude_deg IS NOT NULL
        AND a.longitude_deg IS NOT NULL
    ),

    distancias AS (
        SELECT
            cp.cidade_pesquisada,
            ab.iata_code,
            ab.nome_aeroporto,
            ab.cidade_aeroporto,
            ab.tipo_aeroporto,

            6371 * ACOS(
                LEAST(
                    1,
                    GREATEST(
                        -1,
                        COS(RADIANS(cp.latitude_cidade))
                        * COS(RADIANS(ab.latitude_deg))
                        * COS(RADIANS(ab.longitude_deg) - RADIANS(cp.longitude_cidade))
                        + SIN(RADIANS(cp.latitude_cidade))
                        * SIN(RADIANS(ab.latitude_deg))
                    )
                )
            ) AS distancia_km

        FROM cidades_pesquisadas cp
        CROSS JOIN aeroportos_brasileiros ab
    )

    SELECT
        cidade_pesquisada::TEXT AS "Cidade pesquisada",
        COALESCE(iata_code, 'Não informado')::TEXT AS "Código IATA",
        nome_aeroporto::TEXT AS "Nome do aeroporto",
        cidade_aeroporto::TEXT AS "Cidade do aeroporto",
        ROUND(distancia_km::NUMERIC, 2) AS "Distância em km",
        tipo_aeroporto::TEXT AS "Tipo do aeroporto"
    FROM distancias
    WHERE distancia_km <= 100
    ORDER BY
        cidade_pesquisada,
        distancia_km;
END;
$$
LANGUAGE plpgsql;


-- ============================================================
-- 1. Escuderias cadastradas e quantidade de pilotos
-- ============================================================

CREATE OR REPLACE FUNCTION relatorio_escuderias_quantidade_pilotos()
RETURNS TABLE (
    "Escuderia" TEXT,
    "Quantidade de pilotos" BIGINT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.name::TEXT AS "Escuderia",
        COUNT(DISTINCT res.driver_id) AS "Quantidade de pilotos"
    FROM constructors c
    LEFT JOIN results res
        ON res.constructor_id = c.id
    GROUP BY c.id, c.name
    ORDER BY c.name;
END;
$$
LANGUAGE plpgsql;


-- ============================================================
-- 2. Corridas por circuito e estatísticas de voltas
-- ============================================================

CREATE OR REPLACE FUNCTION relatorio_circuitos_estatisticas_voltas()
RETURNS TABLE (
    "ID do circuito" INTEGER,
    "Circuito" TEXT,
    "Quantidade de corridas" BIGINT,
    "Mínimo de voltas" INTEGER,
    "Média de voltas" NUMERIC,
    "Máximo de voltas" INTEGER
)
AS $$
BEGIN
    RETURN QUERY
    WITH voltas_por_corrida AS (
        SELECT
            race_id,
            MAX(laps) AS voltas_registradas
        FROM results
        GROUP BY race_id
    )

    SELECT
        c.id AS "ID do circuito",
        c.name::TEXT AS "Circuito",
        COUNT(DISTINCT r.id) AS "Quantidade de corridas",
        MIN(v.voltas_registradas)::INTEGER AS "Mínimo de voltas",
        ROUND(AVG(v.voltas_registradas)::NUMERIC, 2) AS "Média de voltas",
        MAX(v.voltas_registradas)::INTEGER AS "Máximo de voltas"
    FROM circuits c
    JOIN races r
        ON r.circuit_id = c.id
    LEFT JOIN voltas_por_corrida v
        ON v.race_id = r.id
    GROUP BY c.id, c.name
    ORDER BY c.name;
END;
$$
LANGUAGE plpgsql;


-- ============================================================
-- 3. Corridas de um circuito selecionado
-- ============================================================

CREATE OR REPLACE FUNCTION relatorio_corridas_por_circuito(
    p_circuito_id INTEGER
)
RETURNS TABLE (
    "Corrida" TEXT,
    "Data" DATE,
    "Voltas registradas" INTEGER,
    "Quantidade de pilotos participantes" BIGINT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.race_name::TEXT AS "Corrida",
        r.race_date AS "Data",
        COALESCE(MAX(res.laps), 0)::INTEGER AS "Voltas registradas",
        COUNT(DISTINCT res.driver_id) AS "Quantidade de pilotos participantes"
    FROM races r
    LEFT JOIN results res
        ON res.race_id = r.id
    WHERE r.circuit_id = p_circuito_id
    GROUP BY r.id, r.race_name, r.race_date
    ORDER BY r.race_date;
END;
$$
LANGUAGE plpgsql;