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

    # O id_original do usuário do tipo Piloto corresponde ao id da tabela drivers
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
        "de participação e lista as corridas em que houve pontuação."
    )

    if st.button("Gerar relatório", key="btn_pontos_piloto"):
        try:
            # Relatório 6:
            # Chama a função armazenada no PostgreSQL
            # A função restringe os dados ao piloto logado por meio do driver_id
            df_corridas = executar_consulta("""
                SELECT *
                FROM fn_relatorio6_piloto(%s);
            """, (driver_id,))

            if df_corridas.empty:
                st.info("Nenhuma corrida com pontuação encontrada para este piloto.")
                return

            # Renomeia as colunas da interface
            df_corridas = df_corridas.rename(columns={
                "ano": "Ano",
                "corrida": "Corrida",
                "circuito": "Circuito",
                "data_corrida": "Data",
                "pontos": "Pontos obtidos",
                "posicao_final": "Posição final"
            })

            # Cria o resumo anual a partir das corridas pontuadas retornadas pela função
            df_resumo = (
                df_corridas
                .groupby("Ano", as_index=False)
                .agg({
                    "Pontos obtidos": "sum",
                    "Corrida": "count"
                })
                .rename(columns={
                    "Pontos obtidos": "Total de pontos",
                    "Corrida": "Corridas com pontos"
                })
            )

            st.markdown("### Resumo de pontos por ano")

            st.dataframe(
                df_resumo,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.markdown("### Corridas em que os pontos foram obtidos")

            # Para cada ano, mostra as corridas pontuadas daquele ano
            for _, linha in df_resumo.iterrows():
                ano = int(linha["Ano"])
                total_pontos = linha["Total de pontos"]
                corridas_com_pontos = linha["Corridas com pontos"]

                with st.expander(
                    f"Ano {ano} — Total de pontos: {total_pontos} | Corridas com pontos: {corridas_com_pontos}"
                ):
                    df_ano = df_corridas[df_corridas["Ano"] == ano]

                    st.dataframe(
                        df_ano[[
                            "Corrida",
                            "Circuito",
                            "Data",
                            "Pontos obtidos",
                            "Posição final"
                        ]],
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
            # Relatório 7:
            # Chama a função armazenada no PostgreSQL
            df = executar_consulta("""
                SELECT *
                FROM fn_relatorio7_piloto_status(%s);
            """, (driver_id,))

            if df.empty:
                st.info("Nenhum resultado encontrado para este piloto.")
            else:
                df = df.rename(columns={
                    "status": "Status",
                    "quantidade": "Quantidade de resultados"
                })

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:
            st.error("Erro ao gerar o relatório de resultados por status.")
            st.exception(e)