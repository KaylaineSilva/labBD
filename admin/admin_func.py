from db import conectar
import pandas as pd
import streamlit as st


'''
Nome: consultas
Descrição: com base no tipo, define qual será a query e executa a consulta tratando possíveis erros
Parâmetros:
    - tipo: valor inteiro que define qual consulta será realizada
Retorno: 
    - resultado da consulta caso seja bem sucedido
    - False: caso ocorra erro
'''
def consultas(tipo, parametros=None):
    query = ""

    if tipo == 0:
        #Consulta sobre corridas mais recentes
    
        query = """ 
            SELECT
                r.race_name AS "Corrida",
                c.name AS "Circuito",
                r.race_date AS "Data",
                COALESCE(r.race_time::text, 'Não informado') AS "Horário",
                COUNT(res.id) AS "Quantidade de resultados",
                MAX(res.laps) AS "Quantidade de voltas"
            FROM races r
            LEFT JOIN circuits c
                ON c.id = r.circuit_id
            LEFT JOIN results res
                ON res.race_id = r.id
            WHERE r.season_id = (
                SELECT season_id
                FROM races
                WHERE race_date IS NOT NULL
                ORDER BY race_date DESC
                LIMIT 1
            )
            GROUP BY
                r.id,
                r.race_name,
                c.name,
                r.race_date,
                r.race_time
            ORDER BY r.race_date;
        """
    elif tipo == 1:
        query = """
            SELECT 
                c.name AS "Escuderia",
                SUM(res.points) AS "Pontos Obtidos"
                FROM constructors c
                JOIN results res
                    ON res.constructor_id=c.id
                JOIN races r
                    ON r.id=res.race_id
                JOIN seasons s 
                    ON s.id=r.season_id
                WHERE r.season_id = (
                        SELECT id
                        FROM seasons 
                        ORDER BY year DESC
                        LIMIT 1
                    )
                GROUP BY 
                    c.id, 
                    c.name
                
                ORDER BY SUM(res.points) DESC;
        """

    elif tipo == 2:
        query = """
            SELECT 
                CONCAT(d.given_name, ' ', d.family_name) AS "Piloto",
                SUM(res.points) AS "Pontos Obtidos"
                FROM drivers d
                JOIN results res
                    ON res.driver_id=d.id
                JOIN races r
                    ON res.race_id=r.id
                JOIN seasons s
                    ON r.season_id=s.id
                WHERE s.id= (
                        SELECT id
                        FROM seasons 
                        ORDER BY year DESC
                        LIMIT 1
                    )
                GROUP BY 
                        d.id, 
                        d.given_name,
                        d.family_name
                    
                ORDER BY SUM(res.points) DESC;

        """
    
    elif tipo == 3:
        query = """
            SELECT
                s.status AS "Status",
                COUNT(*) AS "Quantidade de resultados"
            FROM results r
            JOIN status s
                ON s.id = r.status_id
            GROUP BY s.id, s.status
            ORDER BY "Quantidade de resultados" DESC;
        """
    
    try:
        return executar_consulta(query)
        
    except Exception as e:
        st.write(e)
        return False

'''
Nome: executar_consulta 
Descrição: função que isola a conexão com o banco para executar consultas
Parâmetros:
    - query: consulta a ser executada
    - params: parâmetros da consulta, por default None
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
Descrição: função para executar consultas em que o retorno não será em formato de tabela
Parâmetros:
    - query: consulta a ser executada
    - params: parâmetros da consulta, por default None
Retorno: resultado da consulta
'''
def buscar_valor_unico(query, params=None):
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)
    valor = cur.fetchone()[0]

    cur.close()
    conn.close()

    return valor