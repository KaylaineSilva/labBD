import streamlit as st
import pandas as pd
from db import conectar

from admin.admin_func import consultas, buscar_valor_unico


def mostrar_dashboard_admin(usuario):
    st.title("Dashboard do Administrador")

    st.write(f"Usuário logado: **{usuario['login']}**")
    st.write("Perfil: **Administrador do sistema**")

    st.divider()

    try:
        total_pilotos = buscar_valor_unico("""
            SELECT COUNT(*)
            FROM drivers;
        """)

        total_escuderias = buscar_valor_unico("""
            SELECT COUNT(*)
            FROM constructors;
        """)

        total_temporadas = buscar_valor_unico("""
            SELECT COUNT(DISTINCT season_id)
            FROM races;
        """)

        col1, col2, col3 = st.columns(3)

        col1.metric("Total de pilotos", total_pilotos)
        col2.metric("Total de escuderias", total_escuderias)
        col3.metric("Total de temporadas", total_temporadas)

    except Exception as e:
        st.error("Erro ao carregar os totais do dashboard.")
        st.exception(e)
        return

    st.divider()

    
    #Consultas necessárias no dashboard do administrador:
    # 0: Lista das corridas cadastradas na temporada mais recente da base, com circuito, data, horário e quantidade de voltas registrada nos resultados.
    # 1: Lista das escuderias que correram na temporada mais recente da base, cada uma com o total de pontos obtidos.
    # 2: Lista dos pilotos que correram na temporada mais recente da base, cada um com o total de pontos obtidos.
    ano_temporada = buscar_valor_unico("SELECT MAX(year) FROM seasons")

    st.subheader("Corridas da temporada mais recente")
    df_corridas = consultas(0)
    
    if df_corridas.empty:
        st.warning("Nenhuma corrida encontrada para a temporada mais recente.")
    else:
        #Exibir acima o ano da temporada mais recente
        st.write(f"Temporada: {ano_temporada}")
        st.dataframe(df_corridas, width='stretch')

    st.divider()
    
    st.subheader("Escuderias da temporada mais recente por pontuação")

    df_escuderias = consultas(1)

    if df_escuderias.empty:
        st.warning("Nenhuma escuderia encontrada para a temporada mais recente.")
    else:
        #Exibir acima o ano da temporada mais recente
        st.write(f"Temporada: {ano_temporada}")
        st.dataframe(df_escuderias, width='stretch')
    
    st.divider()

    st.subheader("Pilotos da temporada mais recente por pontuação")
    df_pilotos = consultas(2)

    if df_pilotos.empty:
        st.warning("Nenhum piloto encontrado para a temporada mais recente.")
    else:
        #Exibir acima o ano da temporada mais recente
        st.write(f"Temporada: {ano_temporada}")
        st.dataframe(df_pilotos, width='stretch')