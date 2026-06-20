import streamlit as st

from escuderia.escuderia_func import consultas


def mostrar_dashboard_escuderia(usuario):
    st.title("Dashboard da Escuderia")

    st.write(f"Usuário logado: **{usuario['login']}**")
    st.write("Perfil: **Escuderia**")

    constructor_id = usuario["id_original"]

    try:
        df = consultas(0, (constructor_id,))

        if df.empty:
            st.warning("Nenhuma informação encontrada para esta escuderia.")
            return

        dados = df.iloc[0]

        nome_escuderia = dados["Escuderia"]
        quantidade_vitorias = dados["Quantidade de vitórias"]
        quantidade_pilotos = dados["Quantidade de pilotos"]
        primeiro_ano = dados["Primeiro ano"]
        ultimo_ano = dados["Último ano"]

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