import streamlit as st
import pandas as pd
from db import conectar


def mostrar_acoes(usuario):
    st.title("Ações")

    tipo = usuario["tipo"]

    if tipo == "Escuderia":
        acoes_escuderia(usuario)

    # elif tipo == "Piloto":
    #     st.info("Usuários do tipo Piloto podem apenas visualizar dashboards e relatórios.")

def executar_consulta(query, params=None):
    conn = conectar()
    cur = conn.cursor()

    cur.execute(query, params)

    dados = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return pd.DataFrame(dados, columns=colunas)

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
        
def acoes_escuderia(usuario):
    st.subheader("Ações da Escuderia")

    aba1, aba2 = st.tabs(["Consultar piloto por sobrenome", "Inserir pilotos por arquivo"])

    with aba1:
        st.markdown("### Consultar piloto por sobrenome")

        sobrenome = st.text_input("Sobrenome do piloto")

        if st.button("Consultar piloto"):
            if sobrenome.strip() == "":
                st.warning("Digite um sobrenome para consultar.")
            else:
                try:
                    df = executar_consulta("""
                        SELECT *
                        FROM consultar_piloto_escuderia_por_sobrenome(%s, %s);
                    """, (usuario["id_original"], sobrenome.strip()))

                    if df.empty:
                        st.info("Nenhum piloto com esse sobrenome correu por esta escuderia.")
                    else:
                        st.dataframe(df, use_container_width=True, hide_index=True)

                except Exception as e:
                    st.error("Erro ao consultar piloto.")
                    st.exception(e)

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
                st.dataframe(df, use_container_width=True, hide_index=True)

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
                    st.dataframe(df_resultado, use_container_width=True, hide_index=True)

            except Exception as e:
                st.error("Erro ao ler ou processar o arquivo enviado.")
                st.exception(e)
