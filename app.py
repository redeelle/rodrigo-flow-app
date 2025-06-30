import streamlit as st
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import pandas as pd
import json

# --- Configuração Inicial do Streamlit ---
st.set_page_config(
    layout="wide",
    page_title="RODRIGO.FLOW™ - Performance Simbólica",
    page_icon="🧠"
)

# --- CONFIGURAÇÃO DA OPENAI ---
# Buscando a chave da OpenAI dos Streamlit Secrets.
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("Erro: A chave da OpenAI (OPENAI_API_KEY) não foi encontrada nos secrets do Streamlit. Por favor, adicione-a.")
    st.stop()

# --- CONEXÃO COM O FIREBASE ---
if not firebase_admin._apps:
    try:
        # Buscando a chave do Firebase dos Streamlit Secrets.
        # A chave deve ser o JSON completo da conta de serviço, como string.
        firebase_credentials_json_string = st.secrets["FIREBASE_SERVICE_ACCOUNT_KEY"]
        
        # Carrega a string JSON para um dicionário Python.
        # O Streamlit já garante que as quebras de linha da private_key (se for o caso) sejam mantidas.
        service_account_info = json.loads(firebase_credentials_json_string)

        # Usa o dicionário para criar as credenciais e inicializar o app Firebase.
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
    except KeyError:
        st.error("Erro: A chave do Firebase (FIREBASE_SERVICE_ACCOUNT_KEY) não foi encontrada nos secrets do Streamlit. Por favor, adicione-a.")
        st.info("Certifique-se de colar o JSON COMPLETO, baixado do Firebase, no Streamlit Secrets, entre aspas triplas ('''...''').")
        st.stop()
    except json.JSONDecodeError as e:
        st.error(f"Erro ao decodificar o JSON do Firebase: {e}")
        st.info("Verifique se o JSON da chave do Firebase nos Streamlit Secrets está correto. Provavelmente, falta uma aspa tripla ou há um erro na formatação JSON.")
        st.exception(e)
        st.stop()
    except Exception as e:
        st.error(f"Erro inesperado ao inicializar Firebase: {e}")
        st.info("Verifique as credenciais do Firebase nos Streamlit secrets.")
        st.exception(e)
        st.stop()

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
            'nome_vendedor': nome_vendedor,
            'data_hora': data_atual
        })
        st.success("Interação salva com sucesso no banco de dados!")
    except Exception as e:
        st.error(f"Falha ao salvar a interação: {e}")

# --- FUNÇÃO PARA LER TODOS OS DADOS DO FIREBASE ---
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
            df['data_hora'] = pd.to_datetime(df['data_hora'])
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados do Firebase: {e}")
        return pd.DataFrame()


# --- INÍCIO DA INTERFACE DO STREAMLIT ---

tab_vendedor, tab_gestor = st.tabs(["Vendedor (Análise Rápida)", "Gestor (Painel de Performance)"])

with tab_vendedor:
    st.header("🧠 RODRIGO.FLOW™: Seu Treinador de Vendas Pessoal")
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

                st.session_state['ia_response_completa'] = ia_response
                st.session_state['input_do_vendedor'] = user_input
                st.session_state['vendedor_nome'] = vendedor_nome

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

    if 'ia_response_completa' in st.session_state:
        st.markdown("---")
        st.subheader("💡 Hora da Ação!")
        st.write("Você aplicou a estratégia sugerida? Isso é vital para sua evolução!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim, apliquei!", key="btn_apliquei_vendedor"):
                salvar_interacao(
                    st.session_state['input_do_vendedor'],
                    st.session_state['perfil_ia_parsed'],
                    st.session_state['reacao_ia_parsed'],
                    st.session_state['estrategia_ia_parsed'],
                    st.session_state['dica_ia_parsed'],
                    "Sim",
                    st.session_state.get('vendedor_nome', "Não informado")
                )
                for key_to_del in ['ia_response_completa', 'input_do_vendedor', 'perfil_ia_parsed', 
                                    'reacao_ia_parsed', 'estrategia_ia_parsed', 'dica_ia_parsed', 'vendedor_nome']:
                    if key_to_del in st.session_state:
                        del st.session_state[key_to_del]
                st.rerun()

        with col2:
            if st.button("❌ Ainda não / Não se aplica", key="btn_nao_se_aplica_vendedor"):
                salvar_interacao(
                    st.session_state['input_do_vendedor'],
                    st.session_state['perfil_ia_parsed'],
                    st.session_state['reacao_ia_parsed'],
                    st.session_state['estrategia_ia_parsed'],
                    st.session_state['dica_ia_parsed'],
                    "Não",
                    st.session_state.get('vendedor_nome', "Não informado")
                )
                for key_to_del in ['ia_response_completa', 'input_do_vendedor', 'perfil_ia_parsed', 
                                    'reacao_ia_parsed', 'estrategia_ia_parsed', 'dica_ia_parsed', 'vendedor_nome']:
                    if key_to_del in st.session_state:
                        del st.session_state[key_to_del]
                st.rerun()

with tab_gestor:
    st.header("📊 Painel de Performance RODRIGO.FLOW™ do Gestor")
    st.markdown("Visão Estratégica e Simbólica do Desempenho do Time de Vendas.")

    st.subheader("Atualização de Dados")
    if st.button("🔄 Carregar/Atualizar Dados Mais Recentes", key="btn_recarregar_dados"):
        st.cache_data.clear()
        st.rerun()

    dados_interacoes = carregar_dados_interacoes()

    if dados_interacoes.empty:
        st.info("Nenhum dado de interação encontrado para exibir o painel. Incentive seus vendedores a usar a aba 'Vendedor'!")
    else:
        st.subheader("📅 Filtrar por Período")
        min_date_available = dados_interacoes['data_hora'].min().date() if not dados_interacoes.empty else datetime.date.today()
        max_date_available = dados_interacoes['data_hora'].max().date() if not dados_interacoes.empty else datetime.date.today()

        col_start_date, col_end_date = st.columns(2)
        with col_start_date:
            start_date = st.date_input("Data de Início", value=min_date_available, min_value=min_date_available, max_value=max_date_available, key="start_date_filter")
        with col_end_date:
            end_date = st.date_input("Data Final", value=max_date_available, min_value=min_date_available, max_value=max_date_available, key="end_date_filter")

        dados_filtrados = dados_interacoes[
            (dados_interacoes['data_hora'].dt.date >= start_date) &
            (dados_interacoes['data_hora'].dt.date <= end_date)
        ].copy()

        if dados_filtrados.empty:
            st.warning("Nenhum dado encontrado para o período selecionado.")
        else:
            st.write("---")
            st.header("Visão Geral das Interações Registradas")
            st.dataframe(dados_filtrados.sort_values(by='data_hora', ascending=False), use_container_width=True)

            st.write("---")
            st.header("🎯 Perfis Comportamentais Detectados")
            if 'perfil_ia' in dados_filtrados.columns:
                contagem_perfis = dados_filtrados['perfil_ia'].value_counts()
                st.bar_chart(contagem_perfis)
            else:
                st.warning("Coluna 'perfil_ia' não encontrada nos dados filtrados.")

            st.write("---")
            st.header("📈 Taxa de Aplicação das Estratégias Sugeridas")
            if 'aplicou_estrategia' in dados_filtrados.columns:
                contagem_aplicacao = dados_filtrados['aplicou_estrategia'].value_counts()
                total_interacoes = contagem_aplicacao.sum()
                if total_interacoes > 0 and 'Sim' in contagem_aplicacao.index:
                    percentual_aplicado = (contagem_aplicacao['Sim'] / total_interacoes) * 100
                    st.metric(label="Percentual de Estratégias Aplicadas", value=f"{percentual_aplicado:.2f}%", 
                            delta=f"{contagem_aplicacao.get('Sim', 0)} de um total de {total_interacoes} interações")
                else:
                    st.info("Nenhuma estratégia aplicada ou interação registrada no período.")
                st.bar_chart(contagem_aplicacao)
            else:
                st.warning("Coluna 'aplicou_estrategia' não encontrada nos dados filtrados.")

            st.write("---")
            st.header("🧑‍💻 Desempenho por Vendedor")
            dados_com_nome = dados_filtrados[dados_filtrados['nome_vendedor'] != "Não informado"].copy()

            if not dados_com_nome.empty:
                desempenho_vendedores = dados_com_nome.groupby('nome_vendedor').agg(
                    total_interacoes=('nome_vendedor', 'size'),
                    aplicadas=('aplicou_estrategia', lambda x: (x == 'Sim').sum()),
                    nao_aplicadas=('aplicou_estrategia', lambda x: (x == 'Não').sum()),
                    perfis_dominantes=('perfil_ia', lambda x: x.mode()[0] if not x.mode().empty else 'Não definido')
                ).reset_index()
                desempenho_vendedores['% Aplicadas'] = (desempenho_vendedores['aplicadas'] / desempenho_vendedores['total_interacoes'] * 100).fillna(0).round(2)
                
                st.dataframe(desempenho_vendedores.sort_values(by='% Aplicadas', ascending=False), use_container_width=True)

                st.subheader("🚨 Vendedores em Alerta (Perfis Não Guerreiros predominantes)")
                if 'perfil_ia' in dados_com_nome.columns:
                    alertas_por_vendedor = dados_com_nome[dados_com_nome['perfil_ia'] != 'O Guerreiro'].groupby(['nome_vendedor', 'perfil_ia']).size().unstack(fill_value=0)
                    if not alertas_por_vendedor.empty:
                        st.dataframe(alertas_por_vendedor, use_container_width=True)
                        st.markdown("---")
                        st.bar_chart(alertas_por_vendedor.sum(axis=1).sort_values(ascending=False))
                    else:
                        st.success("🎉 Nenhum perfil não-Guerreiro predominante em alerta no período para vendedores identificados!")
                else:
                    st.warning("Coluna 'perfil_ia' não encontrada para análise de alertas.")
            else:
                st.info("Para ver o desempenho individual por vendedor, peça para os vendedores preencherem o campo 'Seu nome'.")

            st.write("---")
            st.header("🚫 Objeções Mais Comuns")
            if 'input_vendedor' in dados_filtrados.columns:
                st.info("Esta análise é baseada na descrição original do vendedor. Para categorização exata, seria necessário processamento de linguagem natural (NLP) adicional.")
                top_objecoes = dados_filtrados['input_vendedor'].value_counts().head(5)
                if not top_objecoes.empty:
                    st.dataframe(top_objecoes, use_container_width=True)
                    st.bar_chart(top_objecoes)
                else:
                    st.info("Não há objeções registradas no período para análise.")
            else:
                st.warning("Coluna 'input_vendedor' não encontrada para análise de objeções.")

            st.write("---")
            st.header("🔽 Exportar Relatório Detalhado")
            csv_export = dados_filtrados.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar Relatório Completo (CSV)",
                data=csv_export,
                file_name=f"rodrigo_flow_relatorio_{datetime.date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="download_csv_full"
            )
