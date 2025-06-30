import streamlit as st
from openai import OpenAI
import pandas as pd
import datetime

# --- Configuração Inicial do Streamlit ---
st.set_page_config(
    layout="wide",
    page_title="RODRIGO.FLOW™ - Performance Simbólica (DEMO)",
    page_icon="🧠" 
)

# --- CONFIGURAÇÃO DA OPENAI ---
# Buscando a chave da OpenAI dos Streamlit Secrets.
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("Erro: A chave da OpenAI (OPENAI_API_KEY) não foi encontrada nos secrets do Streamlit. Por favor, adicione-a.")
    st.stop() # Interrompe a execução para evitar mais erros


# --- INÍCIO DA INTERFACE DO STREAMLIT ---

# Cria abas para Vendedor e Gestor
tab_vendedor, tab_gestor = st.tabs(["Vendedor (Análise Rápida)", "Gestor (Painel - Demo)"])

# --- CONTEÚDO DA ABA 'VENDEDOR' ---
with tab_vendedor:
    st.header("🧠 RODRIGO.FLOW™: Seu Treinador de Vendas Pessoal (DEMO)")
    st.markdown("Bem-vindo(a), Guerreiro(a)! Conte-me sua batalha mais recente.")

    vendedor_nome = st.text_input("Seu nome (opcional, para relatórios futuros):", key="vendedor_nome_input")
    
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

                # Não salvamos dados para a demo por enquanto.
                st.info("Para a demonstração, os dados não estão sendo salvos. O foco é a interação imediata da IA.")

        else:
            st.warning("Por favor, descreva a objeção para que eu possa ajudar!")

    # Para a demo, não haverá botões de feedback nem salvamento
    # st.markdown("---")
    # st.subheader("💡 Hora da Ação!")
    # st.write("Ações futuras (não ativas na demo): Botões para registrar se a estratégia foi aplicada.")


# --- CONTEÚDO DA ABA 'GESTOR' ---
with tab_gestor:
    st.header("📊 Painel de Performance RODRIGO.FLOW™ do Gestor (DEMO)")
    st.markdown("Visão Estratégica e Simbólica do Desempenho do Time de Vendas.")
    st.warning("**PARA A DEMONSTRAÇÃO:** Este painel será preenchido com dados reais da equipe quando a integração do banco de dados estiver completa. Por enquanto, o foco é a funcionalidade de análise para o vendedor.")

    # Exemplo de como o painel seria, apenas para a demo se quiser
    st.subheader("O que você veria aqui em uma versão completa:")
    st.write("- **Lista de Vendedores e seus Arquétipos Predominantes**")
    st.write("- **Objeções Mais Comuns Registradas**")
    st.write("- **Taxa de Aplicação das Estratégias Sugeridas**")
    st.write("- **Vendedores em Alerta Vermelho (Perfis Não Guerreiros)**")
    st.write("- **Relatórios Exportáveis**")
    st.write("")
    st.info("Para a demo, os relatórios podem ser acompanhados por e-mail ou outras ferramentas de gestão. O importante é o feedback instantâneo para o vendedor.")
