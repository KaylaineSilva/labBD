import streamlit as st
import pandas as pd


def mostrar_acoes(usuario):
    st.title("Ações")

    tipo = usuario["tipo"]

    if tipo == "Escuderia":
        acoes_escuderia(usuario)

    # elif tipo == "Piloto":
    #     st.info("Usuários do tipo Piloto podem apenas visualizar dashboards e relatórios.")

def acoes_escuderia(usuario):
    st.subheader("Ações da Escuderia")

    aba1, aba2 = st.tabs(["Consultar piloto por sobrenome", "Inserir pilotos por arquivo"])

    with aba1:
        st.markdown("### Consultar piloto por sobrenome")

        sobrenome = st.text_input("Sobrenome do piloto")

        if st.button("Consultar piloto"):
            if sobrenome.strip() == "":
                st.warning("Digite um sobrenome para consultar.")
            else:
                st.success("Consulta enviada.")
                st.info(
                    "Aqui a interface chamará uma consulta ao banco para verificar "
                    "se esse piloto já correu pela escuderia logada."
                )

    with aba2:
        st.markdown("### Inserir novos pilotos por arquivo")

        arquivo = st.file_uploader(
            "Envie um arquivo CSV ou TXT com os pilotos",
            type=["csv", "txt"]
        )

        st.caption(
            "Cada linha deve conter: driver_ref, given_name, family_name, date_of_birth e country_id."
        )

        if arquivo is not None:
            try:
                df = pd.read_csv(arquivo)

                st.success("Arquivo carregado com sucesso.")
                st.dataframe(df, use_container_width=True, hide_index=True)

                if st.button("Enviar pilotos para cadastro"):
                    st.info(
                        "Aqui a interface chamará a função de inserção dos pilotos no banco."
                    )

            except Exception as e:
                st.error("Erro ao ler o arquivo enviado.")
                st.exception(e)