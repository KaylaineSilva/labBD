"""
Arquivo: app.py
Descrição: Script principal da aplicação Streamlit.
"""

import streamlit as st
import pandas as pd

from db import conectar

from telas.dashboard_admin import mostrar_dashboard_admin
from telas.dashboard_escuderia import mostrar_dashboard_escuderia
from telas.dashboard_piloto import mostrar_dashboard_piloto

from telas.relatorios_admin import mostrar_relatorios_admin
from telas.relatorios_escuderia import mostrar_relatorios_escuderia
from telas.relatorios_piloto import mostrar_relatorios_piloto

from telas.acoes import mostrar_acoes

st.set_page_config(
    page_title="Sistema Fórmula 1",
    page_icon="🏎️",
    layout="wide"
)


def inicializar_sessao():
    if "logado" not in st.session_state:
        st.session_state.logado = False

    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    if "pagina" not in st.session_state:
        st.session_state.pagina = "Dashboard"


def buscar_id_escuderia(constructor_ref):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM constructors
        WHERE constructor_ref = %s;
    """, (constructor_ref,))

    resultado = cur.fetchone()

    cur.close()
    conn.close()

    if resultado is None:
        return None

    return resultado[0]


def buscar_id_piloto(driver_ref):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM drivers
        WHERE driver_ref = %s;
    """, (driver_ref,))

    resultado = cur.fetchone()

    cur.close()
    conn.close()

    if resultado is None:
        return None

    return resultado[0]


def tela_login():
    st.title("🏎️ Sistema Fórmula 1")
    st.subheader("Login")

    with st.form("form_login"):
        login = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

    if entrar:
        # Autenticação temporária para testar a interface.
        # Depois isso pode ser trocado pela consulta real na tabela USERS.

        if login == "admin" and senha == "admin":
            st.session_state.logado = True
            st.session_state.usuario = {
                "userid": 1,
                "login": "admin",
                "tipo": "Admin",
                "id_original": None
            }
            st.session_state.pagina = "Dashboard"
            st.rerun()

        elif login.endswith("_c"):
            constructor_ref = login.replace("_c", "")

            if senha == constructor_ref:
                constructor_id = buscar_id_escuderia(constructor_ref)

                if constructor_id is None:
                    st.error("Escuderia não encontrada na base.")
                    return

                st.session_state.logado = True
                st.session_state.usuario = {
                    "userid": 2,
                    "login": login,
                    "tipo": "Escuderia",
                    "id_original": constructor_id
                }
                st.session_state.pagina = "Dashboard"
                st.rerun()

            else:
                st.error("Usuário ou senha inválidos.")

        elif login.endswith("_d"):
            driver_ref = login.replace("_d", "")

            if senha == driver_ref:
                driver_id = buscar_id_piloto(driver_ref)

                if driver_id is None:
                    st.error("Piloto não encontrado na base.")
                    return

                st.session_state.logado = True
                st.session_state.usuario = {
                    "userid": 3,
                    "login": login,
                    "tipo": "Piloto",
                    "id_original": driver_id
                }
                st.session_state.pagina = "Dashboard"
                st.rerun()

            else:
                st.error("Usuário ou senha inválidos.")


def menu_lateral():
    usuario = st.session_state.usuario

    with st.sidebar:
        st.title("Menu")

        st.write(f"Usuário: **{usuario['login']}**")
        st.write(f"Perfil: **{usuario['tipo']}**")

        st.divider()

        opcoes = ["Dashboard", "Relatórios"]

        if usuario["tipo"] in ["Admin", "Escuderia"]:
            opcoes.append("Ações")

        #tela para teste.
        if usuario["tipo"] == "Admin":
            opcoes.append("Teste de conexão")

        st.session_state.pagina = st.radio(
            "Escolha uma tela",
            opcoes
        )

        st.divider()

        if st.button("Sair"):
            st.session_state.logado = False
            st.session_state.usuario = None
            st.session_state.pagina = "Dashboard"
            st.rerun()


def tela_teste_conexao():
    """
    Tela auxiliar para testar conexão e visualizar tabelas do banco.
    Essa tela é só para desenvolvimento da interface.
    """

    st.title("Teste de conexão com o banco")

    try:
        conn = conectar()
        cur = conn.cursor()

        # Mostra o search_path atual
        cur.execute("SHOW search_path;")
        search_path = cur.fetchone()[0]

        st.subheader("Schema atual")
        st.code(search_path)

        st.divider()

        # Lista as tabelas disponíveis no schema atual
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = current_schema()
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)

        tabelas = [linha[0] for linha in cur.fetchall()]

        if not tabelas:
            st.warning("Nenhuma tabela encontrada no schema atual.")
            cur.close()
            conn.close()
            return

        tabela_escolhida = st.selectbox(
            "Escolha uma tabela para visualizar",
            tabelas
        )

        limite = st.number_input(
            "Quantidade de registros para mostrar",
            min_value=1,
            max_value=100,
            value=10,
            step=1
        )

        st.divider()

        # Mostra as colunas da tabela escolhida
        st.subheader(f"Colunas da tabela {tabela_escolhida}")

        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = current_schema()
            AND table_name = %s
            ORDER BY ordinal_position;
        """, (tabela_escolhida,))

        colunas_info = cur.fetchall()

        df_colunas = pd.DataFrame(
            colunas_info,
            columns=["Nome da coluna", "Tipo de dado"]
        )

        st.dataframe(df_colunas, use_container_width=True)

        st.divider()

        # Mostra os registros da tabela escolhida
        st.subheader(f"Primeiros registros de {tabela_escolhida}")

        # Aqui não usamos parâmetro para nome de tabela porque PostgreSQL não aceita
        # parametrizar identificadores diretamente.
        # Como a tabela vem de uma lista obtida do próprio banco, o risco é controlado.
        cur.execute(f"SELECT * FROM {tabela_escolhida} LIMIT %s;", (limite,))

        dados = cur.fetchall()
        colunas = [desc[0] for desc in cur.description]

        df = pd.DataFrame(dados, columns=colunas)

        st.dataframe(df, use_container_width=True)

        cur.close()
        conn.close()

    except Exception as e:
        st.error("Erro ao conectar ou consultar o banco.")
        st.exception(e)

def roteador():
    usuario = st.session_state.usuario
    tipo = usuario["tipo"]
    pagina = st.session_state.pagina

    if pagina == "Dashboard":
        if tipo == "Admin":
            mostrar_dashboard_admin(usuario)

        elif tipo == "Escuderia":
            mostrar_dashboard_escuderia(usuario)

        elif tipo == "Piloto":
            mostrar_dashboard_piloto(usuario)

    elif pagina == "Relatórios":
        if tipo == "Admin":
            mostrar_relatorios_admin(usuario)

        elif tipo == "Escuderia":
            mostrar_relatorios_escuderia(usuario)

        elif tipo == "Piloto":
            mostrar_relatorios_piloto(usuario)

    elif pagina == "Teste de conexão":
        tela_teste_conexao()
    
    elif pagina == "Ações":
        mostrar_acoes(usuario)


def main():
    inicializar_sessao()

    if not st.session_state.logado:
        tela_login()
    else:
        menu_lateral()
        roteador()


if __name__ == "__main__":
    main()