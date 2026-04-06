# BancoBot: Chatbot Financeiro Inteligente com IA 🏦🤖

## 1. Visão Geral do Projeto

Este projeto demonstra um chatbot de atendimento ao cliente projetado para um banco digital. O grande diferencial do **BancoBot** é a união da plataforma Groq (garantindo respostas conversacionais instantâneas) com um modelo de Machine Learning embutido, capaz de avaliar propostas de crédito em tempo real.

### Objetivos Principais

* Automatizar o atendimento inicial para serviços bancários como Pix, transferências e simulações.
* Avaliar solicitações de empréstimo automaticamente usando um algoritmo de Árvore de Decisão (Scikit-Learn) baseado no perfil financeiro do usuário.
* Garantir uma velocidade de resposta inferior a 1 segundo para a interface conversacional, utilizando a inferência rápida da Groq.
* Manter a precisão nas regras de negócio financeiras através de um Contexto de Sistema (*System Prompt*) rigoroso.

## 2. Stack Tecnológica e Arquitetura

O BancoBot é construído sobre uma arquitetura robusta e focada em performance e análise de dados:

* **Interface (UI):** Chainlit
* **Orquestração/Lógica:** Python
* **Modelo de Linguagem (LLM):** Groq API (Modelo llama-3.3-70b-versatile)
* **Inteligência Artificial (Machine Learning):** Scikit-Learn, Pandas e NumPy
* **Gestão de Segredos:** python-dotenv

## 3. Guia de Instalação e Execução

Siga os passos abaixo para configurar e iniciar o chatbot em seu ambiente local.

### 3.1. Pré-requisitos

Certifique-se de ter instalado:

* Python (Versão 3.10 ou superior recomendada)
* Uma conta Groq e sua **GROQ_API_KEY**.
* Git (para clonagem do repositório)

### 3.2. Setup do Ambiente

1.  **Clonar o Repositório:**
    ```bash
    git clone [https://github.com/jsumiree/Chatbot2.git]
    cd Chatbot
    ```

2.  **Criar e Ativar o Ambiente Virtual (`venv`):**
    ```bash
    python -m venv venv
    
    # Para Windows (PowerShell):
    .\venv\Scripts\Activate.ps1
    
    # Para Linux/macOS:
    source venv/bin/activate
    ```

3.  **Instalar Dependências:**
    Aqui instalamos tanto as bibliotecas do chatbot quanto as de Machine Learning necessárias para o motor de crédito:
    ```bash
    pip install chainlit groq python-dotenv pandas numpy scikit-learn
    ```

### 3.3. Configuração de Variáveis de Ambiente

Para a segurança de sua chave de API, o projeto utiliza um arquivo `.env` que deve ser ignorado pelo Git (verifique seu `.gitignore`).

1.  **Criar o Arquivo `.env`:** Crie um novo arquivo chamado exatamente `.env` na raiz do projeto (ou copie do `.env.example`, se houver).
2.  **Inserir a Chave:** Edite o arquivo `.env` e insira sua chave de API da Groq:
    ```env
    GROQ_API_KEY=sua_chave_api_aqui
    ```

### 3.4. Execução do Chatbot

Execute o seguinte comando na raiz do projeto, com o ambiente virtual ativado:

```bash
chainlit run BancoBot2.py -w