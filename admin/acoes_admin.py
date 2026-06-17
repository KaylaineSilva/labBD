from datetime import date

import streamlit as st
import pandas as pd

from admin.admin_cadastrar import cadastrar_escuderia, cadastrar_piloto

def mostrar_acoes_admin(usuario):
    st.title("Ações")

    tipo = usuario["tipo"]

    if tipo == "Admin":
        acoes_admin()

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
                if cadastrar_escuderia(st.session_state.usuario["userid"], constructor_ref, name, country_id, wikipedia_url):
                    st.success("Escuderia cadastrada com sucesso.")
                else:                    
                    st.error("Falha ao cadastrar escuderia. Verifique se a referência já existe.")

    with aba2:
        st.markdown("### Cadastrar novo piloto")

        with st.form("form_cadastrar_piloto"):
            driver_ref = st.text_input("Referência do piloto")
            given_name = st.text_input("Nome")
            family_name = st.text_input("Sobrenome")
            date_of_birth = st.date_input(
                "Data de nascimento",
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
            country_id = st.number_input("ID do país do piloto", min_value=1, step=1)

            enviar = st.form_submit_button("Cadastrar piloto")

        if enviar:
            if driver_ref.strip() == "" or given_name.strip() == "" or family_name.strip() == "":
                st.warning("Preencha a referência, o nome e o sobrenome do piloto.")
            else:
                if cadastrar_piloto(st.session_state.usuario["userid"], driver_ref, given_name, family_name, date_of_birth, country_id):
                    st.success("Piloto cadastrado com sucesso.")
                else:
                    st.error("Falha ao cadastrar piloto. Verifique se a referência já existe.")
