'''
Arquivo: admin_cadastrar.py
Descrição: Funções para cadastro de escuderias e pilotos, utilizadas pelo administrador.
'''

import streamlit as st

from db import conectar

'''
Nome: cadastrar_escuderia
Descrição: Realiza o cadastro de uma nova escuderia no sistema, inserindo os dados na tabela constructors. O trigger de inserção deve criar um usuário do tipo "Escuderia" automaticamente. A função verifica se o cadastro foi bem-sucedido, retornando True ou False.
Parâmetros:
    - constructor_ref: referência da escuderia (string)
    - name: nome da escuderia (string)
    - country_id: ID do país da escuderia (inteiro)
    - wikipedia_url: URL da Wikipédia da escuderia (string)
Retorno: Booleano indicando se o cadastro foi bem-sucedido (True) ou se falhou (False)
'''
def cadastrar_escuderia(idadmin, constructor_ref, name, country_id, wikipedia_url):
    # Aqui a função deve realizar a inserção dos dados na tabela constructors

    conn = conectar()
    cur = conn.cursor()
    
    try: #Usando a estrutura try-except-finally porque o trigger pode gerar um erro caso o login já exista, e nesse caso queremos dar rollback na transação e retornar False.
        cur.execute("""
            INSERT INTO constructors (constructor_ref, name, country_id, wikipedia_url)
            VALUES (
                    %s, 
                    %s, 
                    %s, 
                    %s
            )
            RETURNING id;
        """, (constructor_ref, name, country_id, wikipedia_url))

        constructor_id = cur.fetchone()[0] #Pegamos o id da escuderia recém cadastrada, que será usado para verificar se o trigger de inserção do usuário foi acionado corretamente.

        #Aqui, o trigger de inserção na tabela users deve ser acionado, criando um usuário do tipo "Escuderia" com id_original igual ao id da escuderia recém cadastrada. 
        #Caso esse login já exista, o trigger deve gerar um erro e a função deve retornar False, indicando que o cadastro falhou.

        #Aqui vericamos se o cadastro foi bem-sucedido, buscando o id da escuderia recém cadastrada. Se não for encontrado, retornamos False.
        cur.execute("""
            SELECT userid
            FROM users
            WHERE login = %s
              AND tipo = 'Escuderia'
              AND id_original = %s;
        """, (constructor_ref + "_c", constructor_id))

        usuario = cur.fetchone()

        if usuario is None:
            conn.rollback()
            st.error("Erro: trigger de inserção do usuário não funcionou corretamente.")
            return False
        
        #Se chegamos aqui, o cadastro foi bem-sucedido, geramos log e damos commit na transação e retornamos True.
        cur.execute(
            """
            INSERT INTO users_log (userid, acao, data_hora)
            VALUES (%s, %s, NOW());
            """, (idadmin,  f"CADASTRO_ESCUDERIA_{constructor_id}")
        )

        conn.commit()
        return True
    except Exception as e:
        st.error("Erro ao cadastrar escuderia:")
        st.exception(e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def cadastrar_piloto(idmin, driver_ref, given_name, family_name, date_of_birth, country_id):
    
    conn = conectar()
    cur = conn.cursor()

    try: #Usando a estrutura try-except-finally porque o trigger pode gerar um erro caso o login já exista, e nesse caso queremos dar rollback na transação e retornar False.
        cur.execute("""
            INSERT INTO drivers (driver_ref, given_name, family_name, date_of_birth, nationality)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (driver_ref, given_name, family_name, date_of_birth, country_id))

        driver_id = cur.fetchone()[0] #Pegamos o id do piloto recém cadastrado, que será usado para verificar se o trigger de inserção do usuário foi acionado corretamente.

        #Aqui, o trigger de inserção na tabela users deve ser acionado, criando um usuário do tipo "Escuderia" com id_original igual ao id da escuderia recém cadastrada. 
        #Caso esse login já exista, o trigger deve gerar um erro e a função deve retornar False, indicando que o cadastro falhou.

        #Verificando se o cadastro foi bem-sucedido, buscando o id do piloto recém cadastrado. Se não for encontrado, retornamos False.
        cur.execute("""
            SELECT userid
            FROM users
            WHERE id_original = %s;
        """, (driver_id))
        
        usuario = cur.fetchone()

        if usuario is None:
            conn.rollback()
            st.error("Erro: trigger de inserção do usuário não funcionou corretamente.")
            return False
        
        #Se chegamos aqui, o cadastro foi bem-sucedido, geramos log e damos commit na transação e retornamos True.
        cur.execute(
            """
            INSERT INTO users_log (userid, acao, data_hora)
            VALUES (%s, %s, NOW());
            """, (idmin,  f"CADASTRO_PILOTO_{driver_id}")
        )
        conn.commit()
        return True
    except Exception as e:
        st.error("Erro ao cadastrar piloto:")
        st.exception(e)
        conn.rollback()
        retorno = False
    finally:
        cur.close()
        conn.close()

    return retorno