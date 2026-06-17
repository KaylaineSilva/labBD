import streamlit as st
import pandas as pd
from db import conectar


def buscar_linha_unica(query, params=None):
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)
    linha = cur.fetchone()

    cur.close()
    conn.close()

    return linha


def executar_consulta(query, params=None):
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)

    dados = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return pd.DataFrame(dados, columns=colunas)


def mostrar_dashboard_piloto(usuario):
    st.title("Dashboard do Piloto")

    driver_id = usuario["id_original"]

    try:
        dados_piloto = buscar_linha_unica("""
            SELECT
                d.given_name || ' ' || d.family_name AS nome_piloto,
                COALESCE(c.name, 'Não informado') AS escuderia_mais_recente,
                EXTRACT(YEAR FROM MIN(r.race_date))::int AS primeiro_ano,
                EXTRACT(YEAR FROM MAX(r.race_date))::int AS ultimo_ano
            FROM drivers d
            LEFT JOIN results res
                ON res.driver_id = d.id
            LEFT JOIN races r
                ON r.id = res.race_id
            LEFT JOIN constructors c
                ON c.id = (
                    SELECT res2.constructor_id
                    FROM results res2
                    JOIN races r2
                        ON r2.id = res2.race_id
                    WHERE res2.driver_id = d.id
                    ORDER BY r2.race_date DESC
                    LIMIT 1
                )
            WHERE d.id = %s
            GROUP BY d.id, d.given_name, d.family_name, c.name;
        """, (driver_id,))

        if dados_piloto is None:
            st.warning("Nenhuma informação encontrada para este piloto.")
            return

        nome_piloto = dados_piloto[0]
        escuderia_mais_recente = dados_piloto[1]
        primeiro_ano = dados_piloto[2]
        ultimo_ano = dados_piloto[3]

        st.subheader(f"Piloto: {nome_piloto}")
        st.write(f"Escuderia associada: **{escuderia_mais_recente}**")

        col1, col2 = st.columns(2)

        col1.metric("Primeiro ano na base", primeiro_ano)
        col2.metric("Último ano na base", ultimo_ano)

    except Exception as e:
        st.error("Erro ao carregar o resumo do piloto.")
        st.exception(e)
        return

    st.divider()

    try:
        st.subheader("Desempenho por ano e circuito")

        df_desempenho = executar_consulta("""
            SELECT
                EXTRACT(YEAR FROM r.race_date)::int AS "Ano",
                c.name AS "Circuito",
                SUM(res.points) AS "Pontos obtidos",
                COUNT(*) FILTER (WHERE res.position_order = 1) AS "Vitórias",
                COUNT(*) AS "Total de corridas"
            FROM results res
            JOIN races r
                ON r.id = res.race_id
            JOIN circuits c
                ON c.id = r.circuit_id
            WHERE res.driver_id = %s
            GROUP BY
                EXTRACT(YEAR FROM r.race_date),
                c.id,
                c.name
            ORDER BY
                "Ano",
                "Circuito";
        """, (driver_id,))

        if df_desempenho.empty:
            st.info("Este piloto ainda não possui resultados cadastrados.")
        else:
            st.dataframe(df_desempenho, use_container_width=True)

    except Exception as e:
        st.error("Erro ao carregar o desempenho do piloto.")
        st.exception(e)