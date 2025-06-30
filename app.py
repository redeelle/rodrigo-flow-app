import streamlit as st
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import pandas as pd
import json # Importa para lidar com a chave do Firebase vinda dos secrets

# --- Configuração Inicial do Streamlit ---
st.set_page_config(
    layout="wide",
    page_title="RODRIGO.FLOW™ - Performance Simbólica",
    page_icon=""
)

# --- CONFIGURAÇÃO DA OPENAI ---
# Substitua "SUA_CHAVE_AQUI" pela sua chave real da OpenAI.
# Recomenda-se usar st.secrets["OPENAI_API_KEY"] para ambientes de produção online.
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", "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"))


# --- CONEXÃO COM O FIREBASE ---
# Esta função inicializa o Firebase Admin SDK.
# Ela verifica se o aplicativo Firebase já foi inicializado para evitar erros
# de dupla inicialização, comuns em apps Streamlit.
if not firebase_admin._apps:
    try:
        # ATENÇÃO: Para deploy online (Streamlit Cloud), a chave do Firebase deve vir dos st.secrets.
        # No seu secrets.toml ou nas configurações de secrets do Streamlit Cloud,
        # adicione uma entrada como:
        # FIREBASE_SERVICE_ACCOUNT_KEY = """{"type": "service_account", "project_id": "...", etc.}"""
        # (O conteúdo COMPLETO do seu firebase_key.json, formatado como string, entre """ """)

        # Carrega as credenciais a partir do conteúdo JSON do segredo do Streamlit
        firebase_credentials_json = st.secrets["FIREBASE_SERVICE_ACCOUNT_KEY"]
        cred = credentials.Certificate(json.loads(firebase_credentials_json))
        firebase_admin.initialize_app(cred)
        # st.sidebar.success("Conexão com Firebase estabelecida.") # Opcional: para depuração
    except Exception as e:
        st.error(f"Erro ao inicializar Firebase: {e}")
        st.info("Verifique as credenciais do Firebase nos Streamlit secrets.")

# Conecta ao Firestore Database
db = firestore.client()


# --- FUNÇÃO PARA SALVAR DADOS NO FIREBASE ---
def salvar_interacao(vendedor_input, ia_perfil, ia_reacao, ia_estrategia, ia_dica, aplicou_estrategia, nome_vendedor="Não informado"):
    try:
        doc_ref = db.collection('interacoes_vendedores').document()
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        doc_ref.set({
            'input_vendedor': vendedor_input,
            'perfil_ia': ia_perfil,
            'reacao_ia': ia_reacao,
            'estrategia_ia': ia_estrategia,
            'mini_treinamento_ia': ia_dica,
            'aplicou_estrategia': aplicou_estrategia,
            'nome_vendedor': nome_vendedor, # Adicionado campo para nome do vendedor
            'data_hora': data_atual
        })
        st.success("Interação salva com sucesso no banco de dados!")
    except Exception as e:
        st.error(f"Falha ao salvar a interação: {e}")

# --- FUNÇÃO PARA LER TODOS OS DADOS DO FIREBASE ---
# st.cache_data armazena em cache os resultados desta função,
# o que significa que ela não será executada novamente (e não fará uma nova chamada ao Firebase)
# a menos que seus parâmetros mudem ou o cache seja limpo explicitamente.
@st.cache_data
def carregar_dados_interacoes():
    try:
        docs = db.collection('interacoes_vendedores').stream()
        dados = []
        for doc in docs:
            item = doc.to_dict()
            dados.append(item)
        
        if dados:
            df = pd.DataFrame(dados)
            # Converte a coluna 'data_hora' para datetime para facilitar ordenação/filtragem
            df['data_hora'] = pd.to_datetime(df['data_hora'])
            return df
        else:
            return pd.DataFrame() # Retorna um DataFrame vazio se não houver dados
    except Exception as e:
        st.error(f"Erro ao carregar dados do Firebase: {e}")
        return pd.DataFrame()


# --- INÍCIO DA INTERFACE DO STREAMLIT ---

# Cria abas para Vendedor e Gestor
tab_vendedor, tab_gestor = st.tabs(["Vendedor (Análise Rápida)", "Gestor (Painel de Performance)"])

# --- CONTEÚDO DA ABA 'VENDEDOR' ---
with tab_vendedor:
    st.header("RODRIGO.FLOW™: Seu Treinador de Vendas Pessoal")
    st.markdown("Bem-vindo(a), Guerreiro(a)! Conte-me sua batalha mais recente.")

    vendedor_nome = st.text_input("Seu nome (opcional, para relatórios):", key="vendedor_nome_input")
    
    user_input = st.text_area(
        "Qual foi a objeção que você recebeu? Descreva sua reação e a do cliente (se puder):",
        height=150,
        placeholder="Ex: 'O cliente disse que o produto era caro e eu fiquei sem saber o que responder.' ou 'Ele disse que não era o momento, e eu desisti na hora.'",
        key="user_input_area"
    )

    if st.button("Analisar Objeção e Receber Estratégia", key="btn_analisar_vendedor"):
        if user_input:
            with st.spinner("Analisando sua batalha e traçando sua estratégia..."):
                prompt_completo = f"""
                Você é o Rodrigo.FLOW™, um especialista em performance comercial e psicologia analítica.
                Seu objetivo é detectar perfis simbólicos (arquétipos de Jung e PNL) de vendedores com base na descrição de uma objeção de vendas e oferecer uma resposta estratégica, empática e um mini-treinamento comportamental.
                Sua linguagem deve ser humana, acolhedora, direta e motivadora, como um treinador emocional, focado em empoderar o vendedor. Nunca seja robótico ou genérico.

                Aqui estão os arquétipos que você deve identificar e as características de cada um para sua análise:
                - O Medroso: Recua nação à pressão, evita confronto direto, busca validação externa para agir, teme a rejeição ou o fracasso.
                - O Sabotador: Autossabota na hora de fechar, dá desconto sem necessidade ou antes da hora, tem medo do sucesso e de não ser merecedor.
                - O Executor: É eficiente e busca resultados, mas impaciente, tende a perder o emocional rápido, impõe soluções sem ouvir.
                - O Diplomata: Tenta agradar demais e perde poder de negociação, evita o atrito, busca harmonia a todo custo, não é assertivo.
                - O Sedutor: Depende da lábia, evita estrutura e preparação, foca na persuasão vazia, sem profundidade, apenas superficial.
                - O Desfocado: Não ouve o cliente, fala demais, perde o fio da meada, falta de presença e de atenção plena.
                - O Visionário: Promete além da conta, foca em um futuro distante sem lidar com a objeção presente ou a realidade do cliente.
                - O Guerreiro: Perfil ideal. Foco, resiliência, equilíbrio entre técnica e emoção, busca a solução real para o cliente, não o ego, enfrenta desafios com coragem.

                **Siga este processo rigorosamente para cada análise:**
                1.  **Detecção Simbólica:** Identifique o arquétipo mais provável que o vendedor demonstrou em sua reação ou na descrição da objeção. Seja preciso. Se a combinação de elementos indica mais de um arquétipo, destaque o dominante.
                2.  **Análise Rápida da Reação:** Explique de forma simples e direta por que ele se comportou daquele jeito, conectando à característica do arquétipo. Ex: "Você recuou porque o medo de perder a venda o paralisou."
                3.  **Sugestão Estratégica (Script):** Crie uma frase ou roteiro prático que o vendedor possa usar para contornar a objeção ou continuar a negociação. A frase deve ter a intenção de fortalecer o vendedor (lembrando-o de seu poder interno) e ser altamente aplicável à situação.
                4.  **Mini-treinamento Simbólico (1 Dica Comportamental):** Ofereça uma única dica curta, prática e de impacto de PNL/comportamento para o vendedor melhorar imediatamente. A dica deve reforçar a atitude do "Guerreiro".
                5.  **Formato de Saída:** Sua resposta DEVE SEGUIR ESTE FORMATO EXATO, usando **títulos em negrito** e em português. Não adicione nenhum texto antes ou depois deste formato:
                    ```
                    **RODRIGO.FLOW™ ANALISA:**
                    **1. Perfil Detectado:** [SEU ARCHETYTPE AQUI. Ex: O Medroso]
                    **2. Sua Reação:** [SUA ANÁLISE PARA O VENDEDOR AQUI]
                    **3. A Estratégia Que Funciona:** [SUA SUGESTÃO DE SCRIPT AQUI]
                    **4. Aja Como Um Guerreiro (Dica Essencial!):** [SUA DICA DE MINI-TREINAMENTO AQUI]
                    ```

                Agora, analise a seguinte situação do vendedor:
                {user_input}
                """

                response_openai = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Você é o Rodrigo.FLOW™, um treinador simbólico de vendas. Sua missão é empoderar vendedores através de insights psicológicos e estratégias práticas."},
                        {"role": "user", "content": prompt_completo}
                    ],
                    temperature=0.7
                )

                ia_response = response_openai.choices[0].message.content
                st.markdown(ia_response)

                # Guarda a resposta COMPLETA da IA e o input original na "sessão" do Streamlit
                st.session_state['ia_response_completa'] = ia_response
                st.session_state['input_do_vendedor'] = user_input
                st.session_state['vendedor_nome'] = vendedor_nome # Guarda o nome do vendedor também

                # Extrai os pedaços da resposta da IA para salvar separadamente
                perfil_ia = "Não identificado"
                reacao_ia = "Não identificado"
                estrategia_ia = "Não identificado"
                dica_ia = "Não identificado"

                for line in ia_response.split('\n'):
                    if line.startswith("**1. Perfil Detectado:**"):
                        perfil_ia = line.replace("**1. Perfil Detectado:**", "").strip()
                    elif line.startswith("**2. Sua Reação:**"):
                        reacao_ia = line.replace("**2. Sua Reação:**", "").strip()
                    elif line.startswith("**3. A Estratégia Que Funciona:**"):
                        estrategia_ia = line.replace("**3. A Estratégia Que Funciona:**", "").strip()
                    elif line.startswith("**4. Aja Como Um Guerreiro (Dica Essencial!):**"):
                        dica_ia = line.replace("**4. Aja Como Um Guerreiro (Dica Essencial!):**", "").strip()

                st.session_state['perfil_ia_parsed'] = perfil_ia
                st.session_state['reacao_ia_parsed'] = reacao_ia
                st.session_state['estrategia_ia_parsed'] = estrategia_ia
                st.session_state['dica_ia_parsed'] = dica_ia

        else:
            st.warning("Por favor, descreva a objeção para que eu possa ajudar!")

    # BOTÕES DE FEEDBACK (Só aparecem depois que a IA responde)
    if 'ia_response_completa' in st.session_state:
        st.markdown("---")
        st.subheader("Hora da Ação!")
        st.write("Você aplicou a estratégia sugerida? Isso é vital para sua evolução!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sim, apliquei!", key="btn_apliquei_vendedor"):
                salvar_interacao(
                    st.session_state['input_do_vendedor'],
                    st.session_state['perfil_ia_parsed'],
                    st.session_state['reacao_ia_parsed'],
                    st.session_state['estrategia_ia_parsed'],
                    st.session_state['dica_ia_parsed'],
                    "Sim",
                    st.session_state.get('vendedor_nome', "Não informado") # Pega o nome do vendedor
                )
                # Limpa a sessão para a próxima interação
                for key_to_del in ['ia_response_completa', 'input_do_vendedor', 'perfil_ia_parsed', 
                                    'reacao_ia_parsed', 'estrategia_ia_parsed', 'dica_ia_parsed', 'vendedor_nome']:
                    if key_to_del in st.session_state:
                        del st.session_state[key_to_del]
                st.rerun() # Reruns the app to clear the displayed AI response and buttons

        with col2:
            if st.button("Ainda não / Não se aplica", key="btn_nao_se_aplica_vendedor"):
                salvar_interacao(
                    st.session_state['input_do_vendedor'],
                    st.session_state['perfil_ia_parsed'],
                    st.session_state['reacao_ia_parsed'],
                    st.session_state['estrategia_ia_parsed'],
                    st.session_state['dica_ia_parsed'],
                    "Não",
                    st.session_state.get('vendedor_nome', "Não informado") # Pega o nome do vendedor
                )
                # Limpa a sessão
                for key_to_del in ['ia_response_completa', 'input_do_vendedor', 'perfil_ia_parsed', 
                                    'reacao_ia_parsed', 'estrategia_ia_parsed', 'dica_ia_parsed', 'vendedor_nome']:
                    if key_to_del in st.session_state:
                        del st.session_state[key_to_del]
                st.rerun() # Reruns the app

# --- CONTEÚDO DA ABA 'GESTOR' ---
with tab_gestor:
    st.header("Painel de Performance RODRIGO.FLOW™ do Gestor")
    st.markdown("Visão Estratégica e Simbólica do Desempenho do Time de Vendas.")

    st.subheader("Atualização de Dados")
    # Botão para recarregar os dados do Firebase, limpando o cache
    if st.button("Carregar/Atualizar Dados Mais Recentes", key="btn_recarregar_dados"):
        st.cache_data.clear() # Limpa o cache para forçar a leitura do Firebase
        st.rerun() # Reinicia o app para carregar os novos dados

    dados_interacoes = carregar_dados_interacoes()

    if dados_interacoes.empty:
        st.info("Nenhum dado de interação encontrado para exibir o painel. Incentive seus vendedores a usar a aba 'Vendedor'!")
    else:
        st.subheader("Filtrar por Período")
        # Filtro de data
        min_date = dados_interacoes['data_hora'].min().date() if not dados_interacoes.empty else datetime.date.today()
        max_date = dados_interacoes['data_hora'].max().date() if not dados_interacoes.empty else datetime.date.today()

        col_start_date, col_end_date = st.columns(2)
        with col_start_date:
            start_date = st.date_input("Data de Início", value=min_date, min_value=min_date, max_value=max_date)
        with col_end_date:
            end_date = st.date_input("Data Final", value=max_date, min_value=min_date, max_value=max_date)

        dados_filtrados = dados_interacoes[
            (dados_interacoes['data_hora'].dt.date >= start_date) &
            (dados_interacoes['data_hora'].dt.date <= end_date)
        ].copy() # Usar .copy() para evitar SettingWithCopyWarning

        if dados_filtrados.empty:
            st.warning("Nenhum dado encontrado para o período selecionado.")
        else:
            st.write("---")
            st.header("Visão Geral das Interações Registradas")
            st.dataframe(dados_filtrados.sort_values(by='data_hora', ascending=False)) # Exibe todos os dados em formato de tabela, ordenados

            st.write("---")
            st.header("Perfis Comportamentais Detectados")
            if 'perfil_ia' in dados_filtrados.columns:
                contagem_perfis = dados_filtrados['perfil_ia'].value_counts()
                st.bar_chart(contagem_perfis)
            else:
                st.warning("Coluna 'perfil_ia' não encontrada nos dados filtrados.")

            st.write("---")
            st.header("Taxa de Aplicação das Estratégias Sugeridas")
            if 'aplicou_estrategia' in dados_filtrados.columns:
                contagem_aplicacao = dados_filtrados['aplicou_estrategia'].value_counts()
                total_interacoes = contagem_aplicacao.sum()
                if total_interacoes > 0 and 'Sim' in contagem_aplicacao:
                    percentual_aplicado = (contagem_aplicacao['Sim'] / total_interacoes) * 100
                    st.metric(label="Percentual de Estratégias Aplicadas", value=f"{percentual_aplicado:.2f}%", 
                            delta=f"{contagem_aplicacao.get('Sim', 0)} de um total de {total_interacoes}")
                else:
                    st.info("Nenhuma estratégia aplicada ou interação registrada no período.")
                st.bar_chart(contagem_aplicacao)
            else:
                st.warning("Coluna 'aplicou_estrategia' não encontrada nos dados filtrados.")

            st.write("---")
            st.header("Desempenho por Vendedor")
            if 'nome_vendedor' in dados_filtrados.columns:
                # Agrupar por vendedor e contar perfis e aplicações
                desempenho_vendedores = dados_filtrados.groupby('nome_vendedor').agg(
                    total_interacoes=('nome_vendedor', 'size'),
                    aplicadas=('aplicou_estrategia', lambda x: (x == 'Sim').sum()),
                    nao_aplicadas=('aplicou_estrategia', lambda x: (x == 'Não').sum()),
                    perfis_dominantes=('perfil_ia', lambda x: x.mode()[0] if not x.mode().empty else 'Não definido')
                ).reset_index()
                desempenho_vendedores['% Aplicadas'] = (desempenho_vendedores['aplicadas'] / desempenho_vendedores['total_interacoes'] * 100).fillna(0).round(2)
                st.dataframe(desempenho_vendedores.sort_values(by='% Aplicadas', ascending=False))

                # Vendedores em Alerta Vermelho
                st.subheader("Vendedores em Alerta (Perfis Não Guerreiros predominantes)")
                if 'perfil_ia' in dados_filtrados.columns:
                    # Contar as ocorrências de cada perfil por vendedor
                    alertas_por_vendedor = dados_filtrados[dados_filtrados['perfil_ia'] != 'O Guerreiro'].groupby(['nome_vendedor', 'perfil_ia']).size().unstack(fill_value=0)
                    if not alertas_por_vendedor.empty:
                        st.dataframe(alertas_por_vendedor)
                        st.markdown("---")
                        # Gráfico visual de alertas por vendedor
                        st.bar_chart(alertas_por_vendedor.sum(axis=1).sort_values(ascending=False))
                    else:
                        st.success("Nenhum perfil não-Guerreiro predominante em alerta no período!")
                else:
                    st.warning("Coluna 'perfil_ia' não encontrada para análise de alertas.")
            else:
                st.info("Adicione o nome do vendedor nas interações para ver o desempenho individual.")


            # Objeções Mais Comuns
            st.write("---")
            st.header("Objeções Mais Comuns")
            if 'input_vendedor' in dados_filtrados.columns:
                # Uma análise mais profunda de objeções exigiria processamento de linguagem natural
                # Por agora, podemos agrupar pelas anotações mais comuns
                st.info("Esta análise é baseada na descrição original do vendedor. Para categorização exata, seria necessário processamento de linguagem natural adicional.")
                top_objecoes = dados_filtrados['input_vendedor'].value_counts().head(5)
                st.dataframe(top_objecoes)
                st.bar_chart(top_objecoes)
            else:
                st.warning("Coluna 'input_vendedor' não encontrada para análise de objeções.")

            # Relatório Exportável
            st.write("---")
            st.header("Exportar Relatório Detalhado")
            csv_export = dados_filtrados.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar Relatório Completo (CSV)",
                data=csv_export,
                file_name=f"rodrigo_flow_relatorio_{start_date}_a_{end_date}.csv",
                mime="text/csv",
                key="download_csv_full"
            )
