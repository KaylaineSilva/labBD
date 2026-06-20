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
            SELECT *
            FROM dashboard_escuderia(%s);
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

        if primeiro_ano is None or ultimo_ano is None:
            col3.metric("Período na base", "Sem resultados")
        else:
            col3.metric("Período na base", f"{primeiro_ano} - {ultimo_ano}")

    except Exception as e:
        st.error("Erro ao carregar o dashboard da escuderia.")
        st.exception(e)