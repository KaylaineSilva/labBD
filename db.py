'''
Arquivo: db.py
Descrição: Script para conexão com o banco de dados, conectando ao banco de dados PostgreSQL usando a biblioteca psycopg2.
'''

import psycopg2

def conectar():
    conn = psycopg2.connect(
        host="pgdb.icmc.usp.br",
        database="scc241_g01_db",
        port=5432,
        user="scc241_g01",
        password="grupo1_Kaylaine_2026",
        options="-c search_path=projeto_f1"
    )

    return conn

def executar_arquivo_sql(caminho_arquivo):
    conn = conectar()
    cur = conn.cursor()

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            sql = arquivo.read()

        cur.execute(sql)
        conn.commit()
        print("Arquivo SQL executado com sucesso.")

    except Exception as e:
        conn.rollback()
        print("Erro ao executar SQL:")
        print(e)

    finally:
        cur.close()
        conn.close()