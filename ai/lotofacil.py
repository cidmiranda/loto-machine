import random

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import tree
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

df = pd.read_csv('dataset/lotofacil_historico.csv', header=None)
# Renomear as colunas
df.columns = ['concurso', 'data'] + [f'numero_{i}' for i in range(1, 16)]

# 1. Convertendo as colunas de números para listas, ignorando valores inválidos
def convert_to_int(row):
    try:
        # Converte todos os valores da linha para inteiros
        return list(map(int, row))
    except ValueError:
        # Retorna lista vazia caso algum valor não seja inteiro
        return []

# Aplicando a conversão nas colunas de números (começando da coluna 2 até a última)
df['numeros'] = df.iloc[:, 2:].apply(lambda row: convert_to_int(row), axis=1)

# Verificando se algum sorteio tem menos de 15 números e removendo
df = df[df['numeros'].apply(lambda x: len(x) == 15)]

# 2. Frequência dos Números
todos_os_numeros = [num for sublist in df['numeros'] for num in sublist]

frequencia_numeros = pd.Series(todos_os_numeros).value_counts().sort_values(ascending=False)
frequencia_numeros_json = frequencia_numeros.to_dict()
print(frequencia_numeros_json)  # Exibe os 25 números mais sorteados

# 3. Análise de Par/Ímpar
numeros_pares = [num for num in todos_os_numeros if num % 2 == 0]
numeros_impares = [num for num in todos_os_numeros if num % 2 != 0]
pares_impares = {'pares': len(numeros_pares), 'impares': len(numeros_impares)}
print(f"pares_impares: {pares_impares}")

# 4. Números Consecutivos
def contar_consecutivos(sorteios):
    #print(sorteios)
    consecutivos = 0
    for i in range(1, len(sorteios)):
        if sorteios[i] == sorteios[i-1] + 1:
            consecutivos += 1
    return consecutivos

consecutivos = df['numeros'].apply(lambda x: contar_consecutivos(sorted(x)))
#print("\nQuantidade de Números Consecutivos em Cada Sorteio:")
#print(consecutivos)

# 5. Distribuição por Faixa (1-5, 6-10, 11-15, etc.)
faixas = [1, 6, 11, 16, 21, 26]  # Definindo as faixas de números
faixa_counts = {f'{faixas[i]}-{faixas[i+1]-1}': 0 for i in range(len(faixas)-1)}

for numeros in df['numeros']:
    for num in numeros:
        for i in range(len(faixas)-1):
            if faixas[i] <= num < faixas[i+1]:
                faixa_counts[f'{faixas[i]}-{faixas[i+1]-1}'] += 1

print("\nDistribuição por Faixa:")
faixa_numeros = {
    '1-5': faixa_counts['1-5'], '6-10': faixa_counts['6-10'], '11-15': faixa_counts['11-15'], '16-20': faixa_counts['16-20'], '21-25': faixa_counts['21-25']
}
print(faixa_numeros)

# 6. Análise de Somas
df['soma_numeros'] = df['numeros'].apply(sum)
somas_historicas = df['soma_numeros'].tolist()
print("\nSomas dos Números Sorteados em Cada Concurso:")
#print(df[['concurso', 'soma_numeros']])
media_somas = np.mean(somas_historicas)
print(somas_historicas)

# 7. Probabilidade de Sorteio de Cada Número (teórica)
total_sorteios = len(df)
probabilidades = frequencia_numeros / total_sorteios
print("\nProbabilidade de Sorteio de Cada Número (teórica):")
print(probabilidades.head(15))  # Exibe as 15 probabilidades mais altas

# Já foi premiado?
# Função que verifica se uma sequência de 15 números já foi sorteada
def verificar_sequencia(sorteio):
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



#Quais números acertei no concurso?
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

# Exemplo de uso:
sequencia_a_verificar = [1, 2, 3, 4, 5, 8, 10, 11, 15, 16, 18, 21, 22, 24, 25]
concurso_a_verificar = 3339  # Número do concurso a comparar

numeros_acertados = numeros_sorteados_concurso(df, concurso_a_verificar, sequencia_a_verificar)
print(f"Números sorteados no concurso {concurso_a_verificar} que estão na sequência fornecida: {numeros_acertados}")

# Converte faixa para proporções
total_faixas = sum(faixa_numeros.values())
proporcao_faixas = {k: v / total_faixas for k, v in faixa_numeros.items()}

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

def completar_lista(previsao_numeros_lista, tamanho=15):
    # Se a lista estiver vazia, inicia com os números mais frequentes
    if not previsao_numeros_lista:
        previsao_numeros_lista = random.sample(sorted(frequencia_numeros.keys(), key=lambda x: -frequencia_numeros[x]),
                                               tamanho)

    # Remove duplicatas mantendo a ordem
    previsao_sem_repetidos = list(dict.fromkeys(previsao_numeros_lista))

    # Se já tiver 15 números, retorna
    if len(previsao_sem_repetidos) >= tamanho:
        return previsao_sem_repetidos[:tamanho]

    # Criar uma lista ordenada pelos mais frequentes
    numeros_disponiveis = sorted(frequencia_numeros.keys(), key=lambda x: -frequencia_numeros[x])

    # Preenchendo mantendo distribuição par/ímpar
    num_pares = sum(1 for n in previsao_sem_repetidos if n % 2 == 0)
    num_impares = sum(1 for n in previsao_sem_repetidos if n % 2 != 0)

    # Conta distribuição por faixa
    distribuicao_faixa = {k: 0 for k in faixa_numeros.keys()}
    for num in previsao_sem_repetidos:
        distribuicao_faixa[obter_faixa(num)] += 1

    while len(previsao_sem_repetidos) < tamanho:
        for num in numeros_disponiveis:
            if num not in previsao_sem_repetidos:
                faixa = obter_faixa(num)

                # Mantém o equilíbrio de pares/ímpares
                #if (num % 2 == 0 and num_pares < num_impares) or (num % 2 != 0 and num_impares < num_pares):
                #    previsao_sem_repetidos.append(num)
                #    if num % 2 == 0:
                #        num_pares += 1
                #    else:
                #        num_impares += 1

                # Verifica se está dentro da proporção histórica
                if distribuicao_faixa[faixa] < round(proporcao_faixas[faixa] * tamanho):
                    if (num % 2 == 0 and num_pares < num_impares) or (num % 2 != 0 and num_impares < num_pares):
                        previsao_sem_repetidos.append(num)
                        distribuicao_faixa[faixa] += 1
                        if num % 2 == 0:
                            num_pares += 1
                        else:
                            num_impares += 1
                # Se a soma estourar a média histórica, para
                if sum(previsao_sem_repetidos) > media_somas + 10:
                    break

            if len(previsao_sem_repetidos) >= tamanho:
                break

    return previsao_sem_repetidos[:tamanho]

#previsao_numeros_lista = []
#nova_lista = completar_lista(previsao_numeros_lista)
#print("\nLógica para retonar números, baseado nas estatísticas:")
#print(sorted(nova_lista))

# Exemplo de sequência a ser verificada
#sequencia_a_verificar = sorted(nova_lista)

# Verificar se a sequência já foi sorteada
#if verificar_sequencia(sequencia_a_verificar):
#    print("Essa sequência já foi sorteada.")
#else:
#    print("Essa sequência nunca foi sorteada.")