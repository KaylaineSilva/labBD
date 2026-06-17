import streamlit as st
from db import conectar


def buscar_linha_unica(query, params=None):
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)
    linha = cur.fetchone()

    cur.close()
    conn.close()

    return linha


def mostrar_dashboard_escuderia(usuario):
    st.title("Dashboard da Escuderia")

    constructor_id = usuario["id_original"]

    try:
        dados = buscar_linha_unica("""
            SELECT
                c.name AS nome_escuderia,
                COUNT(*) FILTER (WHERE res.position_order = 1) AS quantidade_vitorias,
                COUNT(DISTINCT res.driver_id) AS quantidade_pilotos,
                EXTRACT(YEAR FROM MIN(r.race_date))::int AS primeiro_ano,
                EXTRACT(YEAR FROM MAX(r.race_date))::int AS ultimo_ano
            FROM constructors c
            LEFT JOIN results res
                ON res.constructor_id = c.id
            LEFT JOIN races r
                ON r.id = res.race_id
            WHERE c.id = %s
            GROUP BY c.id, c.name;
        """, (constructor_id,))

        if dados is None:
            st.warning("Nenhuma informação encontrada para esta escuderia.")
            return

        nome_escuderia = dados[0]
        quantidade_vitorias = dados[1]
        quantidade_pilotos = dados[2]
        primeiro_ano = dados[3]
        ultimo_ano = dados[4]

        st.subheader(f"Escuderia: {nome_escuderia}")

        col1, col2, col3 = st.columns(3)

        col1.metric("Quantidade de vitórias", quantidade_vitorias)
        col2.metric("Pilotos associados", quantidade_pilotos)
        col3.metric("Período na base", f"{primeiro_ano} - {ultimo_ano}")

    except Exception as e:
        st.error("Erro ao carregar o dashboard da escuderia.")
        st.exception(e)