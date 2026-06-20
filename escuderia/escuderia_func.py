from db import conectar
import pandas as pd
import streamlit as st


'''
Nome: consultas
Descrição: com base no tipo, define qual consulta da escuderia será executada.
Parâmetros:
    - tipo: valor inteiro que define qual consulta será realizada
    - parametros: tupla com os parâmetros da consulta
Retorno:
    - resultado da consulta em formato de DataFrame
    - DataFrame vazio caso ocorra erro
'''
def consultas(tipo, parametros=None):
    query = ""

    if tipo == 0:
        # Dashboard da escuderia
        query = """
            SELECT *
            FROM dashboard_escuderia(%s);
        """

    elif tipo == 1:
        # Ação: consultar piloto por sobrenome dentro da escuderia logada
        query = """
            SELECT *
            FROM consultar_piloto_escuderia_por_sobrenome(%s, %s);
        """

    elif tipo == 2:
        # Relatório 4: vitórias por piloto da escuderia
        query = """
            SELECT *
            FROM relatorio_escuderia_vitorias_pilotos(%s);
        """

    elif tipo == 3:
        # Relatório 5: quantidade de resultados por status da escuderia
        query = """
            SELECT *
            FROM relatorio_escuderia_status(%s);
        """

    else:
        return pd.DataFrame()

    try:
        return executar_consulta(query, parametros)

    except Exception as e:
        st.write(e)
        return pd.DataFrame()


'''
Nome: executar_consulta
Descrição: isola a conexão com o banco para executar consultas SELECT.
Parâmetros:
    - query: consulta SQL a ser executada
    - params: parâmetros da consulta
Retorno: resultado da consulta convertido em DataFrame
'''
def executar_consulta(query, params=None):
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)

    dados = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return pd.DataFrame(dados, columns=colunas)


'''
Nome: buscar_valor_unico
Descrição: executa uma consulta que retorna apenas um valor.
Parâmetros:
    - query: consulta SQL a ser executada
    - params: parâmetros da consulta
Retorno: valor retornado pela consulta ou None
'''
def buscar_valor_unico(query, params=None):
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)
    resultado = cur.fetchone()

    cur.close()
    conn.close()

    if resultado is None:
        return None

    return resultado[0]