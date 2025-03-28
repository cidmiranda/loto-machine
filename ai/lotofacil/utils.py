import random

import pandas as pd


def read_data_set():
    df = pd.read_csv('../dataset/lotofacil_historico.csv', header=None)
    # Renomear as colunas
    df.columns = ['concurso', 'data'] + [f'numero_{i}' for i in range(1, 16)]
    # Aplicando a conversão nas colunas de números (começando da coluna 2 até a última)
    df['numeros'] = df.iloc[:, 2:].apply(lambda row: convert_to_int(row), axis=1)
    # Verificando se algum sorteio tem menos de 15 números e removendo
    df = df[df['numeros'].apply(lambda x: len(x) == 15)]
    return df


def convert_to_int(row):
    try:
        # Converte todos os valores da linha para inteiros
        return list(map(int, row))
    except ValueError:
        # Retorna lista vazia caso algum valor não seja inteiro
        return []


def contar_consecutivos(sorteios):
    # print(sorteios)
    consecutivos = 0
    for i in range(1, len(sorteios)):
        if sorteios[i] == sorteios[i - 1] + 1:
            consecutivos += 1
    return consecutivos


# Função que verifica se uma sequência de 15 números já foi sorteada
def verificar_sequencia(sorteio, df):
    # Garantir que a sequência tenha 15 números
    if len(sorteio) != 15:
        raise ValueError("A sequência deve ter exatamente 15 números.")

    # Ordenar a sequência para comparar de forma consistente
    sorteio_sorted = sorted(sorteio)

    # Iterar sobre o dataframe e verificar se alguma linha contém a mesma sequência
    for _, row in df.iterrows():
        # Acessar a coluna 'numeros' que já contém a lista dos números sorteados
        sorteio_linha = sorted(row['numeros'])  # Acessando a coluna 'numeros', que já é uma lista
        if sorteio_sorted == sorteio_linha:
            return True  # Sequência encontrada
    return False  # Sequência não encontrada


def numeros_sorteados_concurso(df, concurso, sequencia):
    # Garante que a coluna 'concurso' seja do tipo inteiro
    df['concurso'] = df['concurso'].astype(int)

    # Localiza a linha correspondente ao concurso
    sorteio = df[df['concurso'] == int(concurso)]

    if sorteio.empty:
        return f"Concurso {concurso} não encontrado."

    # Converte os números sorteados em um conjunto
    numeros_sorteados = set(sorteio.iloc[0]['numeros'])

    # Converte a sequência fornecida em um conjunto
    sequencia_set = set(sequencia)

    # Retorna a interseção entre os dois conjuntos (números que foram sorteados)
    return sorted(sequencia_set.intersection(numeros_sorteados))


def obter_faixa(numero):
    if 1 <= numero <= 5:
        return '1-5'
    elif 6 <= numero <= 10:
        return '6-10'
    elif 11 <= numero <= 15:
        return '11-15'
    elif 16 <= numero <= 20:
        return '16-20'
    elif 21 <= numero <= 25:
        return '21-25'


def completar_lista(previsao_numeros_lista, frequencia_numeros, faixa_numeros, proporcao_faixas, media_somas,
                    tamanho=15):
    # Se já tiver 15 números, retorna
    if len(previsao_numeros_lista) >= tamanho:
        return previsao_numeros_lista[:tamanho]
    previsao = list(dict.fromkeys(previsao_numeros_lista))
    # Criar uma lista ordenada pelos mais frequentes
    numeros_disponiveis = sorted(frequencia_numeros.keys(), key=lambda x: -frequencia_numeros[x])
    # Conta distribuição por faixa
    list1 = [1, 2, 3, 4, 5]
    distribuicao_faixa = {k: 0 for k in faixa_numeros.keys()}
    for num in previsao:
        distribuicao_faixa[obter_faixa(num)] += 1
    # print(f"distribuicao_faixa: {distribuicao_faixa}")
    # print(f"faixa_numeros: {faixa_numeros}")
    # Preenchendo mantendo distribuição par/ímpar
    num_pares = sum(1 for n in previsao if n % 2 == 0)
    num_impares = sum(1 for n in previsao if n % 2 != 0)
    # print(f"num_pares: {num_pares}")
    # print(f"num_impares: {num_impares}")
    while len(previsao) < tamanho:
        for num in numeros_disponiveis:
            if num not in previsao:
                faixa = obter_faixa(num)
                # distribuicao_faixa[obter_faixa(num)] += 1
                if distribuicao_faixa[faixa] < proporcao_faixas[faixa] * (tamanho * (random.choice(list1)/tamanho)):
                    # print(f"distribuicao_faixa[faixa]: {distribuicao_faixa[faixa]}")
                    # print(f"proporcao_faixas[faixa] * (tamanho * random.choice(list1): {proporcao_faixas[faixa] * (tamanho * (random.choice(list1)/tamanho))}")
                    if (num % 2 == 0 and num_pares < num_impares) or (num % 2 != 0 and num_impares <= num_pares):
                        previsao.append(num)
                        distribuicao_faixa[faixa] += 1
                        if num % 2 == 0:
                            num_pares += 1
                        else:
                            num_impares += 1
                # Se a soma estourar a média histórica, para
                if sum(previsao) > media_somas + 10:
                    break
            if len(previsao) >= tamanho:
                break
    return previsao[:tamanho]

def completar_lista_random(frequencia_numeros, tamanho=15):
    previsao = random.sample(sorted(frequencia_numeros.keys(), key=lambda x: -frequencia_numeros[x]),
                                           tamanho)
    return previsao[:tamanho]


def faixas():
    df = read_data_set()

    # Distribuição por Faixa (1-5, 6-10, 11-15, etc.)
    faixas = [1, 6, 11, 16, 21, 26]  # Definindo as faixas de números
    faixa_counts = {f'{faixas[i]}-{faixas[i + 1] - 1}': 0 for i in range(len(faixas) - 1)}

    for numeros in df['numeros']:
        for num in numeros:
            for i in range(len(faixas) - 1):
                if faixas[i] <= num < faixas[i + 1]:
                    faixa_counts[f'{faixas[i]}-{faixas[i + 1] - 1}'] += 1

    faixa_numeros = {
        '1-5': faixa_counts['1-5'], '6-10': faixa_counts['6-10'], '11-15': faixa_counts['11-15'],
        '16-20': faixa_counts['16-20'], '21-25': faixa_counts['21-25']
    }
    return faixa_numeros


def frequencias():
    df = read_data_set()
    todos_os_numeros = [num for sublist in df['numeros'] for num in sublist]
    frequencia_numeros = pd.Series(todos_os_numeros).value_counts().sort_values(ascending=False)
    return frequencia_numeros.to_dict()

def somas():
    df = read_data_set()
    df['soma_numeros'] = df['numeros'].apply(sum)
    somas_historicas = df['soma_numeros'].tolist()
    return somas_historicas