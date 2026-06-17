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
    resultado = cur.fetchone()

    cur.close()
    conn.close()

    if resultado is None:
        return None

    return resultado[0]


def mostrar_relatorios_escuderia(usuario):
    st.title("Relatórios da Escuderia")

    constructor_id = usuario["id_original"]

    nome_escuderia = buscar_valor_unico("""
        SELECT name
        FROM constructors
        WHERE id = %s;
    """, (constructor_id,))

    if nome_escuderia is None:
        st.error("Escuderia não encontrada.")
        return

    st.write(f"Usuário logado: **{usuario['login']}**")
    st.write(f"Escuderia: **{nome_escuderia}**")

    relatorio = st.selectbox(
        "Selecione o relatório",
        [
            "Vitórias por piloto da escuderia",
            "Quantidade de resultados por status"
        ]
    )

    st.divider()

    if relatorio == "Vitórias por piloto da escuderia":
        relatorio_vitorias_por_piloto(constructor_id)

    elif relatorio == "Quantidade de resultados por status":
        relatorio_status_escuderia(constructor_id)


def relatorio_vitorias_por_piloto(constructor_id):
    st.subheader("Vitórias por piloto da escuderia")

    st.write(
        "Este relatório lista os pilotos que já correram pela escuderia "
        "e a quantidade de vezes em que alcançaram a primeira posição."
    )

    if st.button("Gerar relatório"):
        try:
            df = executar_consulta("""
                SELECT
                    d.given_name || ' ' || d.family_name AS "Piloto",
                    COUNT(*) FILTER (WHERE res.position_order = 1) AS "Quantidade de vitórias"
                FROM results res
                JOIN drivers d
                    ON d.id = res.driver_id
                WHERE res.constructor_id = %s
                GROUP BY
                    d.id,
                    d.given_name,
                    d.family_name
                ORDER BY
                    "Quantidade de vitórias" DESC,
                    "Piloto";
            """, (constructor_id,))

            if df.empty:
                st.info("Nenhum piloto encontrado para esta escuderia.")
            else:
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:
            st.error("Erro ao gerar o relatório de vitórias por piloto.")
            st.exception(e)


def relatorio_status_escuderia(constructor_id):
    st.subheader("Quantidade de resultados por status")

    st.write(
        "Este relatório mostra a quantidade de resultados por status, "
        "considerando apenas corridas da escuderia logada."
    )

    if st.button("Gerar relatório"):
        try:
            df = executar_consulta("""
                SELECT
                    s.status AS "Status",
                    COUNT(*) AS "Quantidade de resultados"
                FROM results res
                JOIN status s
                    ON s.id = res.status_id
                WHERE res.constructor_id = %s
                GROUP BY
                    s.id,
                    s.status
                ORDER BY
                    "Quantidade de resultados" DESC;
            """, (constructor_id,))

            if df.empty:
                st.info("Nenhum resultado encontrado para esta escuderia.")
            else:
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:
            st.error("Erro ao gerar o relatório de resultados por status.")
            st.exception(e)