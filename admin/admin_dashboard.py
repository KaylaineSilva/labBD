import streamlit as st
import pandas as pd
from db import conectar


def executar_consulta(query, params=None):
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)

    dados = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return pd.DataFrame(dados, columns=colunas)


def buscar_valor_unico(query, params=None):
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)
    valor = cur.fetchone()[0]

    cur.close()
    conn.close()

    return valor


def mostrar_dashboard_admin(usuario):
    st.title("Dashboard do Administrador")

    st.write(f"Usuário logado: **{usuario['login']}**")
    st.write("Perfil: **Administrador do sistema**")

    st.divider()

    try:
        total_pilotos = buscar_valor_unico("""
            SELECT COUNT(*)
            FROM drivers;
        """)

        total_escuderias = buscar_valor_unico("""
            SELECT COUNT(*)
            FROM constructors;
        """)

        total_temporadas = buscar_valor_unico("""
            SELECT COUNT(DISTINCT season_id)
            FROM races;
        """)

        col1, col2, col3 = st.columns(3)

        col1.metric("Total de pilotos", total_pilotos)
        col2.metric("Total de escuderias", total_escuderias)
        col3.metric("Total de temporadas", total_temporadas)

    except Exception as e:
        st.error("Erro ao carregar os totais do dashboard.")
        st.exception(e)
        return

    st.divider()

    try:
        st.subheader("Corridas da temporada mais recente")

        df_corridas = executar_consulta("""
            SELECT
                r.race_name AS "Corrida",
                c.name AS "Circuito",
                r.race_date AS "Data",
                COALESCE(r.race_time::text, 'Não informado') AS "Horário",
                COUNT(res.id) AS "Quantidade de resultados",
                MAX(res.laps) AS "Quantidade de voltas"
            FROM races r
            LEFT JOIN circuits c
                ON c.id = r.circuit_id
            LEFT JOIN results res
                ON res.race_id = r.id
            WHERE r.season_id = (
                SELECT season_id
                FROM races
                WHERE race_date IS NOT NULL
                ORDER BY race_date DESC
                LIMIT 1
            )
            GROUP BY
                r.id,
                r.race_name,
                c.name,
                r.race_date,
                r.race_time
            ORDER BY r.race_date;
        """)

        st.dataframe(df_corridas, width='stretch')

    except Exception as e:
        st.error("Erro ao carregar as corridas da temporada mais recente.")
        st.exception(e)

    st.divider()

    try:
        st.subheader("Escuderias da temporada mais recente por pontuação")

        df_escuderias = executar_consulta("""
            SELECT
                c.name AS "Escuderia",
                SUM(res.points) AS "Total de pontos"
            FROM results res
            JOIN races r
                ON r.id = res.race_id
            JOIN constructors c
                ON c.id = res.constructor_id
            WHERE r.season_id = (
                SELECT season_id
                FROM races
                WHERE race_date IS NOT NULL
                ORDER BY race_date DESC
                LIMIT 1
            )
            GROUP BY c.id, c.name
            ORDER BY "Total de pontos" DESC;
        """)

        st.dataframe(df_escuderias, width='stretch')

    except Exception as e:
        st.error("Erro ao carregar a pontuação das escuderias.")
        st.exception(e)

    st.divider()

    try:
        st.subheader("Pilotos da temporada mais recente por pontuação")

        df_pilotos = executar_consulta("""
            SELECT
                d.given_name || ' ' || d.family_name AS "Piloto",
                SUM(res.points) AS "Total de pontos"
            FROM results res
            JOIN races r
                ON r.id = res.race_id
            JOIN drivers d
                ON d.id = res.driver_id
            WHERE r.season_id = (
                SELECT season_id
                FROM races
                WHERE race_date IS NOT NULL
                ORDER BY race_date DESC
                LIMIT 1
            )
            GROUP BY d.id, d.given_name, d.family_name
            ORDER BY "Total de pontos" DESC;
        """)

        st.dataframe(df_pilotos, width='stretch')

    except Exception as e:
        st.error("Erro ao carregar a pontuação dos pilotos.")
        st.exception(e)