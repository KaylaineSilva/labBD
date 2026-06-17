import streamlit as st
import pandas as pd
from db import conectar


def executar_consulta(query, params=None):
    """
    Executa uma consulta SELECT no banco e retorna o resultado como DataFrame.
    """

    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)

    dados = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return pd.DataFrame(dados, columns=colunas)

def buscar_valor_unico(query, params=None):
    """
    Executa uma consulta que retorna apenas um valor.
    """

    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)
    valor = cur.fetchone()[0]

    cur.close()
    conn.close()

    return valor


def mostrar_relatorios_admin(usuario):
    st.title("Relatórios do Administrador")

    st.write(f"Usuário logado: **{usuario['login']}**")

    relatorio = st.selectbox(
        "Selecione o relatório",
        [
            "Quantidade de resultados por status",
            "Aeroportos próximos a uma cidade brasileira",
            "Relatório hierárquico de escuderias e corridas"
        ]
    )

    st.divider()

    if relatorio == "Quantidade de resultados por status":
        relatorio_resultados_por_status()

    elif relatorio == "Aeroportos próximos a uma cidade brasileira":
        relatorio_aeroportos_por_cidade()

    elif relatorio == "Relatório hierárquico de escuderias e corridas":
        relatorio_hierarquico()


def relatorio_resultados_por_status():
    st.subheader("Quantidade de resultados por status")

    if st.button("Gerar relatório"):
        try:
            df = executar_consulta("""
                SELECT
                    s.status AS "Status",
                    COUNT(*) AS "Quantidade de resultados"
                FROM results r
                JOIN status s
                    ON s.id = r.status_id
                GROUP BY s.id, s.status
                ORDER BY "Quantidade de resultados" DESC;
            """)

            st.caption(
                "Contagem total de resultados agrupados pelo status final de cada participação."
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        except Exception as e:
            st.error("Erro ao gerar o relatório de resultados por status.")
            st.exception(e)


def relatorio_aeroportos_por_cidade():
    st.subheader("Aeroportos próximos a uma cidade brasileira")

    st.write(
        "Informe o nome de uma cidade brasileira. O relatório busca aeroportos brasileiros "
        "dos tipos medium_airport ou large_airport localizados a até 100 km da cidade."
    )

    cidade = st.text_input("Nome da cidade")

    if st.button("Buscar aeroportos"):
        if cidade.strip() == "":
            st.warning("Digite o nome de uma cidade para realizar a busca.")
            return

        cidade_busca = cidade.strip()

        try:
            df = executar_consulta("""
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
                        LOWER(TRIM(%s)),
                        'áàãâäéèêëíìîïóòõôöúùûüç',
                        'aaaaaeeeeiiiiooooouuuuc'
                    )
                    AND (
                        co.code = 'BR'
                        OR co.name ILIKE 'Brazil'
                        OR co.name ILIKE 'Brasil'
                    )
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
                        OR co.name ILIKE 'Brazil'
                        OR co.name ILIKE 'Brasil'
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
                    cidade_pesquisada AS "Cidade pesquisada",
                    COALESCE(iata_code, 'Não informado') AS "Código IATA",
                    nome_aeroporto AS "Nome do aeroporto",
                    cidade_aeroporto AS "Cidade do aeroporto",
                    ROUND(distancia_km::numeric, 2) AS "Distância em km",
                    tipo_aeroporto AS "Tipo do aeroporto"
                FROM distancias
                WHERE distancia_km <= 100
                ORDER BY
                    "Cidade pesquisada",
                    "Distância em km";
            """, (cidade_busca,))

            if df.empty:
                st.info("Nenhum aeroporto encontrado para essa cidade no raio de 100 km.")
            else:
                st.caption(
                    "A distância é calculada em quilômetros a partir das coordenadas da cidade pesquisada e do aeroporto."
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:
            st.error("Erro ao gerar o relatório de aeroportos próximos.")
            st.exception(e)

def relatorio_hierarquico():
    st.subheader("Relatório hierárquico de escuderias e corridas")

    st.write(
        "Este relatório apresenta as escuderias cadastradas e um resumo hierárquico "
        "das corridas registradas na base."
    )

    if st.button("Gerar relatório hierárquico"):
        st.session_state["gerar_relatorio_hierarquico_admin"] = True

    if not st.session_state.get("gerar_relatorio_hierarquico_admin", False):
        return

    try:
        st.divider()

        # ------------------------------------------------------------
        # Parte inicial: escuderias cadastradas e quantidade de pilotos
        # ------------------------------------------------------------
        st.markdown("### Escuderias cadastradas e quantidade de pilotos")

        df_escuderias = executar_consulta("""
            SELECT
                c.name AS "Escuderia",
                COUNT(DISTINCT res.driver_id) AS "Quantidade de pilotos"
            FROM constructors c
            LEFT JOIN results res
                ON res.constructor_id = c.id
            GROUP BY c.id, c.name
            ORDER BY c.name;
        """)

        st.dataframe(
            df_escuderias,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # ------------------------------------------------------------
        # Nível 1: quantidade total de corridas cadastradas
        # ------------------------------------------------------------
        st.markdown("### Nível 1 — Quantidade total de corridas cadastradas")

        total_corridas = buscar_valor_unico("""
            SELECT COUNT(*)
            FROM races;
        """)

        st.metric("Total de corridas cadastradas", total_corridas)

        st.divider()

        # ------------------------------------------------------------
        # Nível 2: quantidade de corridas por circuito
        # com mínimo, média e máximo de voltas
        # ------------------------------------------------------------
        st.markdown("### Nível 2 — Corridas por circuito e estatísticas de voltas")

        df_circuitos = executar_consulta("""
            WITH voltas_por_corrida AS (
                SELECT
                    race_id,
                    MAX(laps) AS voltas_registradas
                FROM results
                GROUP BY race_id
            )

            SELECT
                c.id AS "ID do circuito",
                c.name AS "Circuito",
                COUNT(DISTINCT r.id) AS "Quantidade de corridas",
                MIN(v.voltas_registradas) AS "Mínimo de voltas",
                ROUND(AVG(v.voltas_registradas)::numeric, 2) AS "Média de voltas",
                MAX(v.voltas_registradas) AS "Máximo de voltas"
            FROM circuits c
            JOIN races r
                ON r.circuit_id = c.id
            LEFT JOIN voltas_por_corrida v
                ON v.race_id = r.id
            GROUP BY c.id, c.name
            ORDER BY c.name;
        """)

        if df_circuitos.empty:
            st.info("Nenhum circuito encontrado.")
            return

        st.dataframe(
            df_circuitos.drop(columns=["ID do circuito"]),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # ------------------------------------------------------------
        # Nível 3: corridas de um circuito selecionado
        # mostrando voltas registradas e pilotos participantes
        # ------------------------------------------------------------
        st.markdown("### Nível 3 — Corridas de um circuito selecionado")

        circuitos = dict(
            zip(
                df_circuitos["Circuito"],
                df_circuitos["ID do circuito"]
            )
        )

        circuito_escolhido = st.selectbox(
            "Selecione um circuito",
            list(circuitos.keys())
        )

        circuito_id = circuitos[circuito_escolhido]

        df_corridas = executar_consulta("""
            SELECT
                r.race_name AS "Corrida",
                r.race_date AS "Data",
                COALESCE(MAX(res.laps), 0) AS "Voltas registradas",
                COUNT(DISTINCT res.driver_id) AS "Quantidade de pilotos participantes"
            FROM races r
            LEFT JOIN results res
                ON res.race_id = r.id
            WHERE r.circuit_id = %s
            GROUP BY r.id, r.race_name, r.race_date
            ORDER BY r.race_date;
        """, (circuito_id,))

        st.dataframe(
            df_corridas,
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:
        st.error("Erro ao gerar o relatório hierárquico.")
        st.exception(e)
