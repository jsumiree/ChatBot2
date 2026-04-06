import os
import random as rd
import pandas as pd
import numpy as np
import re  # <--- NOVA BIBLIOTECA: Ajuda o Python a ler textos em busca de padrões
from sklearn.tree import DecisionTreeClassifier
from dotenv import load_dotenv 
import chainlit as cl
from groq import Groq

load_dotenv() 

# =====================================================================
# 1. MÓDULO Scikit-Learn
# criamos um dataframe para simular informações de clientes e logo 
# em seguida treinamos o modelo.
# =====================================================================
def treinar_modelo_credito():
    np.random.seed(42)
    df = pd.DataFrame({
        'Renda_Mensal': np.random.randint(1500, 15000, 1000),
        'Idade': np.random.randint(18, 75, 1000),
        'Score_Serasa': np.random.randint(300, 900, 1000),
        'Divida_Atual': np.random.randint(0, 50000, 1000)
    })
    condicao = (df['Score_Serasa'] > 600) & (df['Renda_Mensal'] > df['Divida_Atual'] * 0.5)
    df['Status'] = np.where(condicao, 1, 0)
    
    modelo = DecisionTreeClassifier(max_depth=3, random_state=42)
    modelo.fit(df[['Renda_Mensal', 'Idade', 'Score_Serasa', 'Divida_Atual']], df['Status'])
    return modelo

def avaliar_cliente(modelo_treinado, renda, idade, score, divida):
    dados_cliente = pd.DataFrame({
        'Renda_Mensal': [renda], 'Idade': [idade], 'Score_Serasa': [score], 'Divida_Atual': [divida]
    })
    resultado = modelo_treinado.predict(dados_cliente)[0]
    return "APROVADO" if resultado == 1 else "NEGADO"

modelo_arvore = treinar_modelo_credito()

# =====================================================================
# 2. CONFIGURAÇÕES DO BANCOBOT
# criamos aleatoriamente o saldo do cliente, o valor do emprestimo e uma
# taxa mensal, logo usamos a formula Tabela price.
# =====================================================================
saldo_na_conta = round(np.random.uniform(1000, 10000), 2)
prestamos = rd.randint(1,10)*1000
taxa = 0.08

Emprestimos = f"""
 * 🎉 PARABÉNS! Seu crédito foi APROVADO pelo nosso sistema de risco.*
 Você tem um limite pré-aprovado de R$ {prestamos}. Veja as opções:
-  1 Parcela............. R$ {(prestamos*taxa)/(1-(1+taxa)**-1):.2f}
-  2 Parcelas............ R$ {(prestamos*taxa)/(1-(1+taxa)**-2):.2f}
-  3 Parcelas............ R$ {(prestamos*taxa)/(1-(1+taxa)**-3):.2f}
-  4 Parcelas............ R$ {(prestamos*taxa)/(1-(1+taxa)**-4):.2f}
-  5 Parcelas............ R$ {(prestamos*taxa)/(1-(1+taxa)**-5):.2f}
"""

Pix = "\n*Área Pix:*\n- Enviar um pix\n- Pix com Cartão\n- Pagar com QR code\n- Copia e Cola\n- Cobrar com chave Pix\n"
MENU = "\n*O que deseja fazer hoje:*\n- Área pix\n- Realizar uma tranferencia\n- Pedir um emprestimo\n"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
GROQ_MODEL = "llama-3.3-70b-versatile" 

# =====================================================================
# 3. INTERFACE E LÓGICA DO CHATBOT (Chainlit)
# =====================================================================
@cl.on_chat_start
async def start():
    system_message = (
        "Você é um assistente de atendimento ao cliente para o 'BancoBot'. "
        f"O Cliente tem um saldo na conta de {saldo_na_conta}"
        f"{MENU}"
        f"Se o cliente solicitar Pix, use as informações de {Pix}. "
        "\n\n--- REGRA ESTRITA PARA EMPRÉSTIMOS ---\n"
        "Se o cliente pedir um empréstimo, VOCÊ NÃO PODE OFERECER VALORES AINDA. "
        "Você DEVE obrigatoriamente fazer 4 perguntas ao cliente para análise de risco:\n"
        "1. Qual a sua renda mensal líquida?\n"
        "2. Qual a sua idade?\n"
        "3. Qual é o seu Score no Serasa?\n"
        "4. Qual o valor total das suas dívidas atuais?\n"
        "Faça as perguntas de forma simpática. Você pode perguntar tudo de uma vez ou uma por uma. "
        "QUANDO O CLIENTE RESPONDER OS 4 DADOS, agradeça e coloque EXATAMENTE esta tag no final da sua mensagem (apenas com números): "
        "$$[RENDA, IDADE, SCORE, DIVIDA]$$"
    )
    
    cl.user_session.set("message_history", [{"role": "system", "content": system_message}])
    await cl.Message(content="Olá! Sou o BancoBot. Em que posso ajudar hoje?").send()

@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    
    msg = cl.Message(content="")
    await msg.send()

    try:
        response_stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=message_history,
            temperature=0.3, 
            stream=True,
        )

        full_response = ""
        for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                await msg.stream_token(content)
                full_response += content
                
        await msg.update()
        message_history.append({"role": "assistant", "content": full_response})

       
        padrao_dados = re.search(r'\$\$\[(.*?)\]\$\$', full_response)
        
        if padrao_dados:
            # Extrai os números de dentro dos colchetes
            numeros = padrao_dados.group(1).split(',')
            try:
                renda = float(numeros[0].strip())
                idade = int(numeros[1].strip())
                score = int(numeros[2].strip())
                divida = float(numeros[3].strip())
                
                # CHAMA A INTELIGÊNCIA ARTIFICIAL MATEMÁTICA
                decisao = avaliar_cliente(modelo_arvore, renda, idade, score, divida)
                
                # Devolve a resposta final na tela baseada no cálculo
                if decisao == "APROVADO":
                    await cl.Message(content=Emprestimos).send()
                    message_history.append({"role": "system", "content": "Diga ao usuário que o crédito foi APROVADO."})
                else:
                    negativa = "😔 Poxa... Após passar seus dados pelo nosso algoritmo de risco, seu crédito foi **NEGADO** no momento."
                    await cl.Message(content=negativa).send()
                    message_history.append({"role": "system", "content": "Diga ao usuário que o crédito foi NEGADO."})
                    
            except Exception as e:
                await cl.Message(content="Tivemos um problema ao ler seus dados numéricos. Pode tentar digitar apenas os números?").send()

    except Exception as e:
        await cl.Message(content=f"Ocorreu um erro: {e}").send()