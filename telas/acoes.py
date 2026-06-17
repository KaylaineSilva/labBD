import streamlit as st
import pandas as pd


def mostrar_acoes(usuario):
    st.title("Ações")

    tipo = usuario["tipo"]

    if tipo == "Admin":
        acoes_admin()

    elif tipo == "Escuderia":
        acoes_escuderia(usuario)

    # elif tipo == "Piloto":
    #     st.info("Usuários do tipo Piloto podem apenas visualizar dashboards e relatórios.")


def acoes_admin():
    st.subheader("Ações do Administrador")

    aba1, aba2 = st.tabs(["Cadastrar escuderia", "Cadastrar piloto"])

    with aba1:
        st.markdown("### Cadastrar nova escuderia")

        with st.form("form_cadastrar_escuderia"):
            constructor_ref = st.text_input("Referência da escuderia")
            name = st.text_input("Nome da escuderia")
            country_id = st.number_input("ID do país", min_value=1, step=1)
            wikipedia_url = st.text_input("URL da Wikipédia")

            enviar = st.form_submit_button("Cadastrar escuderia")

        if enviar:
            if constructor_ref.strip() == "" or name.strip() == "":
                st.warning("Preencha pelo menos a referência e o nome da escuderia.")
            else:
                st.success("Dados da escuderia enviados para cadastro.")
                st.info("Aqui a interface chamará a função de inserção na tabela constructors.")

    with aba2:
        st.markdown("### Cadastrar novo piloto")

        with st.form("form_cadastrar_piloto"):
            driver_ref = st.text_input("Referência do piloto")
            given_name = st.text_input("Nome")
            family_name = st.text_input("Sobrenome")
            date_of_birth = st.date_input("Data de nascimento")
            country_id = st.number_input("ID do país do piloto", min_value=1, step=1)

            enviar = st.form_submit_button("Cadastrar piloto")

        if enviar:
            if driver_ref.strip() == "" or given_name.strip() == "" or family_name.strip() == "":
                st.warning("Preencha a referência, o nome e o sobrenome do piloto.")
            else:
                st.success("Dados do piloto enviados para cadastro.")
                st.info("Aqui a interface chamará a função de inserção na tabela drivers.")


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