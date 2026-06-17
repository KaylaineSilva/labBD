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


def mostrar_relatorios_piloto(usuario):
    st.title("Relatórios do Piloto")

    driver_id = usuario["id_original"]

    nome_piloto = buscar_valor_unico("""
        SELECT given_name || ' ' || family_name
        FROM drivers
        WHERE id = %s;
    """, (driver_id,))

    if nome_piloto is None:
        st.error("Piloto não encontrado.")
        return

    st.write(f"Usuário logado: **{usuario['login']}**")
    st.write(f"Piloto: **{nome_piloto}**")

    relatorio = st.selectbox(
        "Selecione o relatório",
        [
            "Pontos por ano e corridas pontuadas",
            "Quantidade de resultados por status"
        ]
    )

    st.divider()

    if relatorio == "Pontos por ano e corridas pontuadas":
        relatorio_pontos_por_ano(driver_id)

    elif relatorio == "Quantidade de resultados por status":
        relatorio_status_piloto(driver_id)


def relatorio_pontos_por_ano(driver_id):
    st.subheader("Pontos por ano e corridas pontuadas")

    st.write(
        "Este relatório apresenta o total de pontos obtidos pelo piloto em cada ano "
        "de participação e, para cada ano, lista as corridas em que houve pontuação."
    )

    if st.button("Gerar relatório", key="btn_pontos_piloto"):
        try:
            # Consulta 1:
            # Total de pontos por ano de participação do piloto logado.
            df_resumo = executar_consulta("""
                SELECT
                    EXTRACT(YEAR FROM r.race_date)::int AS "Ano",
                    SUM(res.points) AS "Total de pontos",
                    COUNT(*) AS "Corridas disputadas",
                    COUNT(*) FILTER (WHERE res.points > 0) AS "Corridas com pontos"
                FROM results res
                JOIN races r
                    ON r.id = res.race_id
                WHERE res.driver_id = %s
                GROUP BY EXTRACT(YEAR FROM r.race_date)
                ORDER BY "Ano";
            """, (driver_id,))

            if df_resumo.empty:
                st.info("Nenhum resultado encontrado para este piloto.")
                return

            st.markdown("### Resumo de pontos por ano")

            st.dataframe(
                df_resumo,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.markdown("### Corridas em que os pontos foram obtidos")

            # Para cada ano, busca apenas as corridas em que o piloto fez pontos.
            for _, linha in df_resumo.iterrows():
                ano = int(linha["Ano"])
                total_pontos = linha["Total de pontos"]
                corridas_com_pontos = linha["Corridas com pontos"]

                with st.expander(
                    f"Ano {ano} — Total de pontos: {total_pontos} | Corridas com pontos: {corridas_com_pontos}"
                ):
                    df_corridas = executar_consulta("""
                        SELECT
                            r.race_name AS "Corrida",
                            c.name AS "Circuito",
                            r.race_date AS "Data",
                            res.points AS "Pontos obtidos",
                            res.position_order AS "Posição final"
                        FROM results res
                        JOIN races r
                            ON r.id = res.race_id
                        JOIN circuits c
                            ON c.id = r.circuit_id
                        WHERE res.driver_id = %s
                        AND EXTRACT(YEAR FROM r.race_date)::int = %s
                        AND res.points > 0
                        ORDER BY r.race_date;
                    """, (driver_id, ano))

                    if df_corridas.empty:
                        st.info("Neste ano, o piloto participou, mas não obteve pontos.")
                    else:
                        st.dataframe(
                            df_corridas,
                            use_container_width=True,
                            hide_index=True
                        )

        except Exception as e:
            st.error("Erro ao gerar o relatório de pontos por ano.")
            st.exception(e)


def relatorio_status_piloto(driver_id):
    st.subheader("Quantidade de resultados por status")

    st.write(
        "Este relatório mostra a quantidade de resultados por status, "
        "considerando apenas as corridas em que o piloto participou."
    )

    if st.button("Gerar relatório", key="btn_status_piloto"):
        try:
            df = executar_consulta("""
                SELECT
                    s.status AS "Status",
                    COUNT(*) AS "Quantidade de resultados"
                FROM results res
                JOIN status s
                    ON s.id = res.status_id
                WHERE res.driver_id = %s
                GROUP BY
                    s.id,
                    s.status
                ORDER BY
                    "Quantidade de resultados" DESC;
            """, (driver_id,))

            if df.empty:
                st.info("Nenhum resultado encontrado para este piloto.")
            else:
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:
            st.error("Erro ao gerar o relatório de resultados por status.")
            st.exception(e)