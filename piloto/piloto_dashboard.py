import streamlit as st
from piloto.piloto_func import buscar_linha_unica, executar_consulta


def mostrar_dashboard_piloto(usuario):
    st.title("Dashboard do Piloto")

    # O id_original do usuário do tipo Piloto corresponde ao id da tabela drivers
    # Esse valor garante que o piloto veja apenas informações sobre si mesmo
    driver_id = usuario["id_original"]

    try:
        # Chamada da função armazenada criada no PostgreSQL
        dados_piloto = buscar_linha_unica("""
            SELECT *
            FROM fn_dashboard_piloto_resumo(%s);
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

        # Chamada da função armazenada responsável pelo desempenho por ano e circuito
        df_desempenho = executar_consulta("""
            SELECT *
            FROM fn_dashboard_piloto_desempenho(%s);
        """, (driver_id,))

        if df_desempenho.empty:
            st.info("Este piloto ainda não possui resultados cadastrados.")
        else:
            # Renomeia as colunas para exibição na interface
            df_desempenho = df_desempenho.rename(columns={
                "ano": "Ano",
                "circuito": "Circuito",
                "pontos": "Pontos obtidos",
                "vitorias": "Vitórias",
                "total_corridas": "Total de corridas"
            })

            st.dataframe(
                df_desempenho,
                width="stretch",
                hide_index=True
            )

    except Exception as e:
        st.error("Erro ao carregar o desempenho do piloto.")
        st.exception(e)