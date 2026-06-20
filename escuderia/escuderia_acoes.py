import streamlit as st
import pandas as pd

from escuderia.escuderia_func import consultas
from escuderia.escuderia_cadastrar import inserir_piloto_arquivo


def mostrar_acoes_escuderia(usuario):
    st.title("Ações")

    tipo = usuario["tipo"]

    if tipo == "Escuderia":
        acoes_escuderia(usuario)


def acoes_escuderia(usuario):
    st.subheader("Ações da Escuderia")

    aba1, aba2 = st.tabs([
        "Consultar piloto por sobrenome",
        "Inserir pilotos por arquivo"
    ])

    with aba1:
        st.markdown("### Consultar piloto por sobrenome")

        sobrenome = st.text_input("Sobrenome do piloto")

        if st.button("Consultar piloto"):
            if sobrenome.strip() == "":
                st.warning("Digite um sobrenome para consultar.")
            else:
                df = consultas(
                    1,
                    (usuario["id_original"], sobrenome.strip())
                )

                if df.empty:
                    st.info("Nenhum piloto com esse sobrenome correu por esta escuderia.")
                else:
                    st.dataframe(
                        df,
                        width='stretch',
                        hide_index=True
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

                colunas_obrigatorias = [
                    "driver_ref",
                    "given_name",
                    "family_name",
                    "date_of_birth",
                    "country_id"
                ]

                if not all(coluna in df.columns for coluna in colunas_obrigatorias):
                    st.error("O arquivo não possui todas as colunas obrigatórias.")
                    st.write("Colunas obrigatórias:", colunas_obrigatorias)
                    return

                st.success("Arquivo carregado com sucesso.")

                st.dataframe(
                    df,
                    width='stretch',
                    hide_index=True
                )

                if st.button("Enviar pilotos para cadastro"):
                    resultados = []

                    for indice, linha in df.iterrows():
                        sucesso, mensagem = inserir_piloto_arquivo(
                            usuario["userid"],
                            str(linha["driver_ref"]).strip(),
                            str(linha["given_name"]).strip(),
                            str(linha["family_name"]).strip(),
                            linha["date_of_birth"],
                            int(linha["country_id"])
                        )

                        resultados.append({
                            "Linha": indice + 1,
                            "Piloto": f"{linha['given_name']} {linha['family_name']}",
                            "Status": "Inserido" if sucesso else "Não inserido",
                            "Mensagem": mensagem
                        })

                    df_resultado = pd.DataFrame(resultados)

                    st.dataframe(
                        df_resultado,
                        width='stretch',
                        hide_index=True
                    )

            except Exception as e:
                st.error("Erro ao ler ou processar o arquivo enviado.")
                st.exception(e)