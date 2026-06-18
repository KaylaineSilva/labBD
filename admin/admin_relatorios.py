import streamlit as st
import pandas as pd
from db import conectar

from admin.admin_func import consultas, executar_consulta, buscar_valor_unico

'''
Nome: mostrar_relatorios_admin
Descrição: controla a exibição dos relatórios e confere se o usuário que está acessando está página é o admin
Parâmetro:
    - usuario: informações do usuário da sessão
Retorno: Sem retorno.
'''
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

'''
Nome: relatorio_resultados_por_status
Descrição: Apresenta o relatório de status realizando a consulta e o tratamento de erros relacionado à funcionalidade.
Parâmetros: Nenhum
Retorno: Nenhum
'''
def relatorio_resultados_por_status():
    st.subheader("Quantidade de resultados por status")

    if st.button("Gerar relatório"):
        res = consultas(3)

        if not res.empty:
            st.caption(
                "Contagem total de resultados agrupados pelo status final de cada participação."
            )

            st.dataframe(
                res,
                width='stretch',
                hide_index=True
            )
        else:
            st.error("Erro ao gerar o relatório de resultados por status.")
'''
Nome: relatorio_aeroportos_por_cidade
Descrição: Apresenta o relatório de aeroportos próximos a cidade fornecida pelo usuário realizando a consulta e o tratamento de erros relacionado à funcionalidade.
Parâmetros: Nenhum
Retorno: Nenhum
'''
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
                SELECT *
                FROM buscar_aeroportos_proximos_brasil(%s);
            """, (cidade_busca,))

            if df.empty:
                st.info("Nenhum aeroporto encontrado para essa cidade no raio de 100 km.")
            else:
                st.caption(
                    "A distância é calculada em quilômetros a partir das coordenadas da cidade pesquisada e do aeroporto."
                )

                st.dataframe(
                    df,
                    width='stretch',
                    hide_index=True
                )

        except Exception as e:
            st.error("Erro ao gerar o relatório de aeroportos próximos.")
            st.exception(e)

'''
Nome: relatorio_hierarquico
Descrição: Apresenta o relatório hierarquico (Lista todas as escuderias cadastradas) realizando a consulta e o tratamento de erros relacionado à funcionalidade.
Parâmetros: Nenhum
Retorno: Nenhum
'''
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
            SELECT *
            FROM relatorio_escuderias_quantidade_pilotos();
        """)

        st.dataframe(
            df_escuderias,
            width='stretch',
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
            SELECT *
            FROM relatorio_circuitos_estatisticas_voltas();
        """)

        if df_circuitos.empty:
            st.info("Nenhum circuito encontrado.")
            return

        st.dataframe(
            df_circuitos.drop(columns=["ID do circuito"]),
            width='stretch',
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
            SELECT *
            FROM relatorio_corridas_por_circuito(%s);
        """, (circuito_id,))

        st.dataframe(
            df_corridas,
            width='stretch',
            hide_index=True
        )

    except Exception as e:
        st.error("Erro ao gerar o relatório hierárquico.")
        st.exception(e)
