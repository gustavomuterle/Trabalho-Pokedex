import streamlit as st
import mysql.connector
import pandas as pd

DB_HOST = "etec local"
DB_USER = "root"
DB_PASSWORD = "123456"
DB_DATABASE = "pokedex_db"


@st.cache_resource(ttl=1800)
def conecta_bd():
    """Tenta abrir a conexão com o MySQL."""
    try:
        db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        return db
    except Exception as e:
        st.error(f"Erro no MySQL: Verifica se o servidor está ativo e se o banco '{DB_DATABASE}' existe.")
        st.error(f"Detalhe do erro: {e}")
        return None

def executa_query(sql, params=None, busca_dados=False):
    """Roda qualquer comando SQL (SELECT, INSERT, etc.)."""
    db = conecta_bd()
    if db is None:
        return None

    cursor = db.cursor()

    try:
        cursor.execute(sql, params)

        if busca_dados:
            dados = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
            return pd.DataFrame(dados, columns=colunas)
        else:
            db.commit() 
            return True

    except Exception as e:
        st.error(f"Deu erro ao rodar o comando SQL: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close() 

def guarda_treinador(nome, cidade):
    """Insere um novo treinador."""
    sql = "INSERT INTO treinadores (nome, cidade) VALUES (%s, %s)"
    valores = (nome, cidade if cidade else None)
    st.cache_data.clear() 
    return executa_query(sql, valores)

@st.cache_data
def pega_treinadores():
    """Pega os nomes e IDs dos treinadores para a seleção."""
    sql = "SELECT id, nome FROM treinadores ORDER BY nome ASC"
    df = executa_query(sql, busca_dados=True)
    if df is None or df.empty:
        return {} 
    treinadores_map = {row['nome']: row['id'] for index, row in df.iterrows()}
    return treinadores_map


def guarda_pokemon(nome, tipo1, tipo2, treinador_id):
    """Insere o Pokémon com seu treinador."""
    sql = "INSERT INTO pokemons (nome, tipo1, tipo2, treinador_id) VALUES (%s, %s, %s, %s)"
    valores = (nome, tipo1, tipo2 if tipo2 else None, treinador_id)

    st.cache_data.clear()
    return executa_query(sql, valores)


@st.cache_data
def lista_pokemons_e_treinadores():
    """Pega a lista completa, juntando Pokémon e o nome do Treinador."""
    sql = """
        SELECT 
            p.id, 
            p.nome, 
            p.tipo1, 
            p.tipo2, 
            t.nome AS treinador_nome
        FROM pokemons p
        JOIN treinadores t ON p.treinador_id = t.id
        ORDER BY p.id DESC
    """
    return executa_query(sql, busca_dados=True)

def area_cadastro_treinador():
    """Formulário para novos Treinadores."""
    with st.form("form_treinador", clear_on_submit=True):
        nome = st.text_input("Nome do Treinador", help="Ex: Ash Ketchum")
        cidade = st.text_input("Cidade de Origem", help="Ex: Pallet")
        enviar = st.form_submit_button("Cadastrar Treinador")

    if enviar:
        if nome.strip():
            nome_formatado = nome.strip().capitalize()
            cidade_formatada = cidade.strip().capitalize() if cidade.strip() else None
            ok = guarda_treinador(nome_formatado, cidade_formatada)
            if ok:
                st.success(f"Treinador **{nome_formatado}** cadastrado! Pronto para capturar.")
        else:
            st.warning("O nome do Treinador não pode ficar em branco.")


def area_cadastro_pokemon():
    """Formulário para Pokémons, com seleção obrigatória do Treinador."""
    tipos = ["Normal", "Fogo", "Água", "Grama", "Elétrico", "Gelo", "Lutador", "Venenoso", "Terra", "Voador", "Psíquico", "Inseto", "Pedra", "Fantasma", "Dragão", "Aço", "Fada", "Sombrio", "Nenhum"]
    
    treinadores_map = pega_treinadores()
    treinadores_nomes = list(treinadores_map.keys())

    with st.form("form_pokemon", clear_on_submit=True):
        st.subheader("Informações Básicas")
        nome = st.text_input("Nome do Pokémon")

        if not treinadores_map:
             st.warning("Atenção: Nenhum Treinador cadastrado. Cadastre um na aba ao lado.")
             treinador_selecionado = None
        else:
             treinador_selecionado = st.selectbox("Quem é o Treinador? (Obrigatório)", treinadores_nomes)

        st.subheader("Detalhes dos Tipos")
        c1, c2 = st.columns(2)

        with c1:
            tipo1 = st.selectbox("Tipo Principal (obrigatório)", tipos[:-1])
        with c2:
            t2 = st.selectbox("Tipo Secundário", tipos, index=len(tipos) - 1)
            tipo2 = None if t2 == "Nenhum" else t2

        enviar = st.form_submit_button("Salvar na Pokédex")

    if enviar:
        if not nome.strip():
            st.warning("Faltou o nome do Pokémon.")
        elif not treinador_selecionado:
            st.error("Precisa selecionar um Treinador, é obrigatório!")
        else:
            nome_formatado = nome.strip().capitalize()
            treinador_id = treinadores_map.get(treinador_selecionado)

            ok = guarda_pokemon(nome_formatado, tipo1, tipo2, treinador_id)
            if ok:
                st.success(f"**{nome_formatado}** cadastrado e associado a **{treinador_selecionado}**.")


def area_visualizar():
    """Mostra a Pokédex completa com os dados."""
    tabela = lista_pokemons_e_treinadores()

    if tabela is None:
        return

    if tabela.empty:
        st.info("Nenhuma criatura registrada ainda. Vamos capturar!")
        return

    st.caption(f"Temos **{len(tabela)}** Pokémons registrados.")
    st.divider()
    
    tabela_display = tabela.copy()
    tabela_display.columns = ["ID", "Nome", "Tipo 1", "Tipo 2", "Treinador"]
    tabela_display["Tipo 2"] = tabela_display["Tipo 2"].fillna("—")
    tabela_display = tabela_display.drop(columns=["ID"]) 

    st.dataframe(tabela_display, use_container_width=True)


def main():
    st.set_page_config(layout="wide")
    st.title("Sistema Pokédex - Treinadores e Pokémons")

    tab1, tab2, tab3 = st.tabs(["Cadastrar Treinador", "Cadastrar Pokémon", "Ver Pokédex Completa"])

    with tab1:
        st.header("Novo Treinador")
        area_cadastro_treinador()

    with tab2:
        st.header("Novo Pokémon")
        area_cadastro_pokemon()

    with tab3:
        st.header("Lista de Todos os Registros")
        area_visualizar()


if __name__ == "__main__":
    main()