'''
Arquivo: auth.py
Descrição: Funções para autenticação do sistema.
'''

import bcrypt
import streamlit as st
from db import conectar

def verificar_senha(senha, senha_hash):
    # Verifica se a senha fornecida corresponde ao hash armazenado

    return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))

def gerar_hash_senha(senha):
    # Gera um hash para a senha fornecida

    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")

'''
Nome: logar
Descrição: Verifica as credenciais do usuário e realiza o login, adicionando o log.
Parâmetros:
    - user: nome de usuário
    - password: senha do usuário
Retorno: 
    - Um dicionário com as informações do usuário em caso de sucesso
    - 0: em caso de usuário não encontrado
    - 1: em caso de senha incorreta
'''
def logar(user, password):
    conn = conectar() #conectar ao banco de dados
    cur = conn.cursor()

    cur.execute(
        """
        SELECT userid, login, password, tipo, id_original
        FROM users 
        WHERE login = %s;""", 
        (user,)
    )

    resultado = cur.fetchone()

    if resultado is None:
        cur.close()
        conn.close()
        return 0
    
    userid, login, senha_hash, tipo, id_original = resultado
    if verificar_senha(password, senha_hash):

        #Adicionando o log de login bem-sucedido
        cur.execute(
            "INSERT INTO users_log (userid, acao, data_hora) VALUES (%s, 'LOGIN', NOW());",
            (userid,)
        )
        conn.commit()

        cur.close()
        conn.close()
        return {
            "userid": userid,
            "login": login,
            "tipo": tipo,
            "id_original": id_original
        }
    else:
        cur.close()
        conn.close()
        return 1
    
'''
Nome: retornar_usuarios_insercao
Descrição: Retorna uma lista de usuários a serem inseridos na tabela users a partir das tabelas escuderias e pilotos.
Parâmetros:
    - cur: cursor do banco de dados
    - comando: comando SQL para selecionar os dados da tabela escuderias ou pilotos
    - tipo: tipo de usuário a ser criado ("Escuderia" ou "Piloto")
Retorno: Uma lista de tuplas contendo os dados dos usuários a serem inseridos (login, password, tipo, id_original)
'''
def retornar_usuarios_insercao(cur, comando, tipo):

    cur.execute(comando)    

    resultado = cur.fetchall()

    usuarios = []
    for id_original, ref in resultado:
        
        login = ref+"_c" if tipo == "Escuderia" else ref+"_d"

        password = gerar_hash_senha(ref)

        usuarios.append((login, password, tipo, id_original))
    
    return usuarios

'''
Nome: logout
Descrição: Realiza o logout do usuário, limpando o estado da sessão e adicionando log.
Parâmetros: Nenhum
Retorno: Nenhum
'''
def logout():
    #Inserir log de logout
    if st.session_state.usuario is not None:
        conn = conectar()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users_log (userid, acao, data_hora) VALUES (%s, 'LOGOUT', NOW());",
            (st.session_state.usuario["userid"],)
        )
        conn.commit()
        cur.close()
        conn.close()

    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.pagina = "Dashboard"
    st.rerun()
    

'''
Nome: inserir_usuarios
Descrição: Insere usuários na tabela users a partir das tabelas escuderias e pilotos, caso a tabela users esteja vazia. O usuário admin é inserido manualmente.
Parâmetros: Nenhum
Retorno: Nenhum
'''
def inserir_usuarios():
    # Função para inserir usuários de no banco de dados a partir das tabelas existentes

    conn = conectar()
    cur = conn.cursor()

    # Verificar se já existem usuários na tabela
    cur.execute("SELECT COUNT(*) FROM users;")
    count = cur.fetchone()[0]

    if count == 0:
        #Inserindo o admin manualmente
        admin_password = gerar_hash_senha("admin")
        
        escuderias = retornar_usuarios_insercao(cur, "SELECT id, constructor_ref FROM constructors;", "Escuderia")
        pilotos = retornar_usuarios_insercao(cur, "SELECT id, driver_ref FROM drivers;", "Piloto")

        usuarios = [("admin", admin_password, "Admin", None)] + escuderias + pilotos

        cur.executemany(
            """
            INSERT INTO users (login, password, tipo, id_original) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (login) DO NOTHING;
            """,
            usuarios
        )

        conn.commit()
    
    cur.close()
    conn.close()
