SET search_path TO projeto_f1;
-- ============================================================
-- FUNÇÃO 1: Resumo do dashboard do piloto
-- ============================================================
-- Retorna:
-- nome completo do piloto
-- escuderia mais recente
-- primeiro ano em que aparece na base
-- último ano em que aparece na base

CREATE OR REPLACE FUNCTION fn_dashboard_piloto_resumo(p_driver_id INTEGER)
RETURNS TABLE (
    nome_piloto TEXT,
    escuderia_mais_recente TEXT,
    primeiro_ano INTEGER,
    ultimo_ano INTEGER
)
LANGUAGE SQL
AS $$
    SELECT
        p.nome_piloto,

        COALESCE(
            (
                SELECT v.escuderia
                FROM vw_piloto_resultados_completos v
                WHERE v.driver_id = p_driver_id
                ORDER BY v.race_date DESC
                LIMIT 1
            ),
            'Não informado'
        ) AS escuderia_mais_recente,

        p.primeiro_ano,
        p.ultimo_ano

    FROM vw_piloto_periodo_base p
    WHERE p.driver_id = p_driver_id;
$$;


-- ============================================================
-- FUNÇÃO 2: Desempenho do piloto por ano e circuito
-- ============================================================
-- Retorna para cada ano e circuito:
-- pontos obtidos
-- quantidade de vitórias
-- total de corridas disputadas

CREATE OR REPLACE FUNCTION fn_dashboard_piloto_desempenho(p_driver_id INTEGER)
RETURNS TABLE (
    ano INTEGER,
    circuito TEXT,
    pontos NUMERIC,
    vitorias BIGINT,
    total_corridas BIGINT
)
LANGUAGE SQL
AS $$
    SELECT
        v.ano,
        v.circuito,
        COALESCE(SUM(v.points), 0)::NUMERIC AS pontos,
        COUNT(*) FILTER (WHERE v.position_order = 1) AS vitorias,
        COUNT(*) AS total_corridas
    FROM vw_piloto_resultados_completos v
    WHERE v.driver_id = p_driver_id
    GROUP BY v.ano, v.circuito
    ORDER BY v.ano, v.circuito;
$$;


-- ============================================================
-- FUNÇÃO 3: Relatório 6 do piloto
-- ============================================================
-- Consulta as corridas em que o piloto obteve pontos
-- A função recebe o id do piloto logado e restringe a consulta usando driver_id

CREATE OR REPLACE FUNCTION fn_relatorio6_piloto(p_driver_id INTEGER)
RETURNS TABLE (
    ano INTEGER,
    corrida TEXT,
    circuito TEXT,
    data_corrida DATE,
    pontos NUMERIC,
    posicao_final INTEGER
)
LANGUAGE SQL
AS $$
    SELECT
        v.ano,
        v.corrida,
        v.circuito,
        v.race_date AS data_corrida,
        v.points::NUMERIC AS pontos,
        v.position_order::INTEGER AS posicao_final
    FROM vw_piloto_resultados_completos v
    WHERE v.driver_id = p_driver_id
      AND v.points > 0
    ORDER BY
        v.ano,
        v.race_date,
        v.corrida;
$$;


-- ============================================================
-- FUNÇÃO 4: Relatório 7 do piloto
-- ============================================================
-- Lista a quantidade de resultados por status nas corridas em que o piloto participou

CREATE OR REPLACE FUNCTION fn_relatorio7_piloto_status(p_driver_id INTEGER)
RETURNS TABLE (
    status TEXT,
    quantidade BIGINT
)
LANGUAGE SQL
AS $$
    SELECT
        v.status,
        COUNT(*) AS quantidade
    FROM vw_piloto_resultados_completos v
    WHERE v.driver_id = p_driver_id
    GROUP BY v.status
    ORDER BY
        quantidade DESC,
        v.status;
$$;
