import asyncio
import requests
from telegram import Bot
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import time
import joblib

token = '6643635778:AAE1_GUSScC7fd2F9u0H-SmAg6ouH21cB60'  # Substitua pelo token real do seu bot
chat_id = '-1001941894388'  # Substitua pelo chat_id real

bot = Bot(token=token)
ultima_lista = []  # Para armazenar a última lista de cores
entrada_confirmada = False  # Flag para verificar se a entrada foi confirmada
lista1 = []
green = []
loss = []
total_partidas = []  # Contador de total de partidas
seguidos = []
# Inicialize o LabelEncoder
encoder = LabelEncoder()
cores_possiveis = ['Vermelho', 'Preto', 'Branco']  # Adicione todas as cores possíveis aqui
encoder.fit(cores_possiveis)

async def enviar_mensagem(mensagem):
    try:
        await bot.send_message(chat_id=chat_id, text=mensagem)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {str(e)}")

async def verificar_entrada(num):
    # Suas condições de entrada aqui
    modelo = treinar_modelo_com_historico(lista1, modelo="modelo_color_predictor.pkl")
            
    # Preveja a próxima cor
    nova_cor_numerica = modelo.predict([encoder.transform([lista1[0]])])
    nova_cor = encoder.inverse_transform(nova_cor_numerica)

    print("A próxima cor mais provável é:", nova_cor[0])
    cor_enviada = nova_cor[0]
    if cor_enviada:
        cor = '🔴' if cor_enviada == 'Vermelho' else '⚫'
        await enviar_mensagem(f'🎯 Entrar no {cor}\nBuscar apoio no ⚪')
        return cor_enviada
    else:
        return None

async def verificar_alteracao_lista_loop():
    global ultima_lista

    while True:
        # Verifique a lista atual
        url = 'https://blaze-1.com/api/roulette_games/recent'
        response = requests.get(url)
        r = response.json()
        lista_atual = []

        for x in range(len(r)):
            val = r[x]['color']
            if val == 1:
                val = 'Vermelho'
            elif val == 2:
                val = 'Preto'
            elif val == 0:
                val = 'Branco'
            lista_atual.append(val)
        print('alteração',lista_atual)

        if lista_atual != ultima_lista:
            ultima_lista = lista_atual  # Atualize a última lista com a lista atual
            lista1.insert(0, lista_atual[0])
            #lista1.append(lista_atual[0])  # Adicione o primeiro item da lista atual à lista1
            print('lista1', lista1)
            break  # Saia do loop se houver uma alteração na lista
        await asyncio.sleep(1)  # Aguarde um segundo antes de verificar novamente

# Função para treinar ou re-treinar o modelo com base no histórico completo
def treinar_modelo_com_historico(historico_cores, modelo=None):
    # Converta o histórico de cores em valores numéricos
    historico_cores_numerico = encoder.transform(historico_cores)

    # Crie as sequências de cores e as próximas cores
    X = []
    y = []
    for i in range(len(historico_cores_numerico) - 1):
        X.append([historico_cores_numerico[i]])
        y.append(historico_cores_numerico[i + 1])

    # Crie um modelo Random Forest ou carregue um modelo existente
    try:
        modelo = joblib.load('modelo_color_predictor.pkl')
    except FileNotFoundError:
        # Se o arquivo não existir, crie um novo modelo
        modelo = RandomForestClassifier(n_estimators=100, random_state=42)

    # Treine o modelo
    modelo.fit(X, y)

    # Salve o modelo treinado em um arquivo
    joblib.dump(modelo, 'modelo_color_predictor.pkl')

    return modelo

async def enviar_placar():
    global green, loss, total_partidas, seguidos
    total_green = len(green)
    total_loss = len(loss)
    total_greens_seguidos = len(seguidos)
    print(seguidos)
    print(total_greens_seguidos)
    total_partidas_jogadas = sum(total_partidas)

    mensagem_placar = f"📊 Placar:\n\nGREENs: {total_green}\nLOSSs: {total_loss}\nTotal de Partidas: {total_partidas_jogadas}\nGreens seguidos: {total_greens_seguidos}"

    await enviar_mensagem(mensagem_placar)

async def resultado(num, num_rodada):
    global ultima_lista, entrada_confirmada, seguidos
    await verificar_alteracao_lista_loop()  
    cor_entrada= await verificar_entrada(num)

    if cor_entrada:

        # Aguarde o tempo da rodada (30 segundos)
        #await asyncio.sleep(20)
        await verificar_alteracao_lista_loop()  # Inicie o loop de verificação da lista

   
        # Consulta a URL novamente para verificar o resultado mais recente
        url = 'https://blaze-1.com/api/roulette_games/recent'
        response = requests.get(url)
        r = response.json()
        
        # Verifica o resultado mais recente
        resultado_recente = r[0]['color']
        
        if resultado_recente == 1:
            cor_recente = '🔴'
        elif resultado_recente == 0:
            cor_recente = '⚪'
        else:
            cor_recente ='⚫'
            
        
        if cor_entrada == 'Vermelho':
            cor_entrada = '🔴' 
        elif cor_entrada == 'Preto':
            cor_entrada = '⚫'
        
        if cor_recente=='⚪':
            cor_entrada = '⚪' 
        
        if cor_recente == cor_entrada or cor_recente=='⚪':   
            await enviar_mensagem(f'✅ GREEN no {cor_entrada}')
            entrada_confirmada = False
            ultima_lista = None
            green.append(cor_entrada)
            seguidos.append(cor_entrada)
            print(seguidos)
        else:
            await enviar_mensagem(f'🔄 Gale - Tentar novamente no {cor_entrada}')
            entrada_confirmada = True  # Marca a entrada como confirmada
            
            if entrada_confirmada:
                # Se já houve uma entrada confirmada e estamos no estado de Gale
               
                await verificar_alteracao_lista_loop()  # Inicie o loop de verificação da lista

                # Consulta a URL novamente para verificar o resultado mais recente
                url = 'https://blaze-1.com/api/roulette_games/recent'
                response = requests.get(url)
                r = response.json()
                
                # Verifica o resultado mais recente
                resultado_recente = r[0]['color']
                if resultado_recente == 1:
                    cor_recente = '🔴'
                elif resultado_recente == 0:
                    cor_recente = '⚪'
                else:
                    cor_recente ='⚫'
                if cor_recente=='⚪':
                    cor_entrada = '⚪' 
                if cor_recente == cor_entrada or cor_recente=='⚪':
                    await enviar_mensagem(f'✅ GREEN no {cor_entrada}')
                    entrada_confirmada = False  # Reinicie para verificar novas entradas
                    ultima_lista = None
                    green.append(cor_entrada)
                    seguidos.append(cor_entrada)
                    print(seguidos)
                else:
                    await enviar_mensagem(f'🔄 Gale - Tentar novamente no {cor_entrada}')
                    entrada_confirmada = True
                    #segundo gale
                    if entrada_confirmada:
                        # Se já houve uma entrada confirmada e estamos no estado de Gale
                    
                        await verificar_alteracao_lista_loop()  # Inicie o loop de verificação da lista

                        # Consulta a URL novamente para verificar o resultado mais recente
                        url = 'https://blaze-1.com/api/roulette_games/recent'
                        response = requests.get(url)
                        r = response.json()
                        
                        # Verifica o resultado mais recente
                        resultado_recente = r[0]['color']
                        if resultado_recente == 1:
                            cor_recente = '🔴'
                        elif resultado_recente == 0:
                            cor_recente = '⚪'
                        else:
                            cor_recente ='⚫'
                        if cor_recente=='⚪':
                            cor_entrada = '⚪' 
                        if cor_recente == cor_entrada or cor_recente=='⚪':
                            await enviar_mensagem(f'✅ GREEN no {cor_entrada}')
                            entrada_confirmada = False  # Reinicie para verificar novas entradas
                            ultima_lista = None
                            green.append(cor_entrada)
                            seguidos.append(cor_entrada)
                            print(seguidos)
                        else:
                            await enviar_mensagem(f'❌ LOSS')
                            entrada_confirmada = False
                            loss.append(cor_entrada)
                            seguidos = []
                            print(seguidos)
        
        total_partidas.append(1)
        await enviar_placar()                
        
    else:
        # Se não houve chance de entrada, enviamos uma mensagem informativa
        await enviar_mensagem(f'⚠️ Não houve chance de entrada')


async def main():
    global ultima_lista
    
    while True:
        # Verifica as listas com mais frequência (por exemplo, a cada 1 segundo)
        url = 'https://blaze-1.com/api/roulette_games/recent'
        response = requests.get(url)
        r = response.json()
        print(r)
        lista_atual = []

        for x in range(len(r)):
            val = r[x]['color']
            if val == 1:
                val = 'Vermelho'
            elif val == 2:
                val = 'Preto'
            elif val == 0:
                val = 'Branco'
            lista_atual.append(val)

        print('main',lista_atual)
        if len(lista1) == 0:
            lista1.extend(lista_atual)
        
        # Verifica se a lista atual é diferente da última lista
        if lista_atual != ultima_lista:
            await verificar_alteracao_lista_loop()
            await resultado(lista_atual, r[0]['color'])  # Adicione o argumento num_rodada aqui
            ultima_lista = lista_atual  # Atualiza a última lista com a lista atual

        # Aguarde um intervalo antes de verificar novamente (por exemplo, 1 segundo)
        await asyncio.sleep(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
