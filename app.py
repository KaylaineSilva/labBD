"""
Arquivo: app.py
Descrição: Script principal da aplicação Streamlit.
"""

import streamlit as st
import pandas as pd
from db import conectar


def main():
    st.title("Projeto Fórmula 1")

    st.write("Exemplo de consulta para verificar a conexão e os dados da tabela drivers")

    try:
        conn = conectar()
        cur = conn.cursor()

        # Verifica o schema usado pela conexão
        cur.execute("SHOW search_path;")
        search_path = cur.fetchone()

        st.subheader("Schema atual")
        st.write(search_path)

        # Verifica quantidade de registros
        cur.execute("SELECT COUNT(*) FROM drivers;")
        qtd_drivers = cur.fetchone()[0]

        st.subheader("Quantidade de pilotos")
        st.write(qtd_drivers)

        # Busca alguns pilotos
        cur.execute("SELECT * FROM drivers LIMIT 10;")
        dados = cur.fetchall()

        # Pega os nomes das colunas automaticamente
        colunas = [desc[0] for desc in cur.description]

        df = pd.DataFrame(dados, columns=colunas) #montar uma tabela com os dados retornados utilizando a biblioteca pandas

        st.subheader("Primeiros registros da tabela drivers")
        st.dataframe(df)

        cur.close()
        conn.close()

    except Exception as e:
        st.error("Erro ao conectar ou consultar o banco.")
        st.exception(e)


main()