from db import conectar


'''
Nome: inserir_piloto_arquivo
Descrição: insere um piloto enviado por arquivo na tabela drivers.
O trigger de drivers deve criar automaticamente o usuário do tipo Piloto.
Parâmetros:
    - userid_escuderia: id do usuário escuderia logado
    - driver_ref: referência do piloto
    - given_name: nome do piloto
    - family_name: sobrenome do piloto
    - date_of_birth: data de nascimento
    - country_id: id do país
Retorno:
    - tupla (True, mensagem) em caso de sucesso
    - tupla (False, mensagem) em caso de erro
'''
def inserir_piloto_arquivo(userid_escuderia, driver_ref, given_name, family_name, date_of_birth, country_id):
    conn = conectar()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id
            FROM drivers
            WHERE LOWER(TRIM(given_name)) = LOWER(TRIM(%s))
              AND LOWER(TRIM(family_name)) = LOWER(TRIM(%s));
        """, (given_name, family_name))

        if cur.fetchone() is not None:
            conn.rollback()
            return False, "Piloto já existe com o mesmo nome e sobrenome."

        cur.execute("""
            INSERT INTO drivers (
                driver_ref,
                given_name,
                family_name,
                date_of_birth,
                country_id
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (driver_ref, given_name, family_name, date_of_birth, country_id))

        driver_id = cur.fetchone()[0]

        cur.execute("""
            SELECT userid
            FROM users
            WHERE login = %s
              AND tipo = 'Piloto'
              AND id_original = %s;
        """, (driver_ref + "_d", driver_id))

        usuario_criado = cur.fetchone()

        if usuario_criado is None:
            conn.rollback()
            return False, "Trigger não criou o usuário do piloto."

        cur.execute("""
            INSERT INTO users_log (userid, acao, data_hora)
            VALUES (%s, %s, NOW());
        """, (userid_escuderia, f"CADASTRO_PILOTO_ARQUIVO_{driver_id}"))

        conn.commit()
        return True, "Piloto inserido com sucesso."

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        cur.close()
        conn.close()