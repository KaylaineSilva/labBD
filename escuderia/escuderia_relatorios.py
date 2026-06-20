import streamlit as st

from escuderia.escuderia_func import consultas, buscar_valor_unico


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

    if st.button("Gerar relatório", key="gerar_relatorio_vitorias_escuderia"):
        df = consultas(2, (constructor_id,))

        if df.empty:
            st.info("Nenhum piloto encontrado para esta escuderia.")
        else:
            st.dataframe(
                df,
                width='stretch',
                hide_index=True
            )


def relatorio_status_escuderia(constructor_id):
    st.subheader("Quantidade de resultados por status")

    st.write(
        "Este relatório mostra a quantidade de resultados por status, "
        "considerando apenas corridas da escuderia logada."
    )

    if st.button("Gerar relatório", key="gerar_relatorio_status_escuderia"):
        df = consultas(3, (constructor_id,))

        if df.empty:
            st.info("Nenhum resultado encontrado para esta escuderia.")
        else:
            st.dataframe(
                df,
                width='stretch',
                hide_index=True
            )