import pandas as pd
from db import conectar


def executar_consulta(query, params=None):
    """
    Executa uma consulta SELECT no banco e retorna o resultado como DataFrame.
    Usada pelos dashboards e relatórios do piloto.
    """
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)

    dados = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return pd.DataFrame(dados, columns=colunas)


def buscar_linha_unica(query, params=None):
    """
    Executa uma consulta que retorna apenas uma linha.
    Usada para buscar o resumo do dashboard do piloto.
    """
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)
    linha = cur.fetchone()

    cur.close()
    conn.close()

    return linha


def buscar_valor_unico(query, params=None):
    """
    Executa uma consulta que retorna apenas um valor.
    Usada para buscar informações simples, como o nome do piloto.
    """
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)
    resultado = cur.fetchone()

    cur.close()
    conn.close()

    if resultado is None:
        return None

    return resultado[0]