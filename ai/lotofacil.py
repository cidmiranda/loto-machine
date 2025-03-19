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
print("Frequência dos Números Sorteados:")
print(frequencia_numeros.head(25))  # Exibe os 25 números mais sorteados

# 3. Análise de Par/Ímpar
numeros_pares = [num for num in todos_os_numeros if num % 2 == 0]
numeros_impares = [num for num in todos_os_numeros if num % 2 != 0]

print("\nDistribuição Par/Ímpar:")
print(f"Total de Pares: {len(numeros_pares)}")
print(f"Total de Ímpares: {len(numeros_impares)}")

# 4. Números Consecutivos
def contar_consecutivos(sorteios):
    #print(sorteios)
    consecutivos = 0
    for i in range(1, len(sorteios)):
        if sorteios[i] == sorteios[i-1] + 1:
            consecutivos += 1
    return consecutivos

consecutivos = df['numeros'].apply(lambda x: contar_consecutivos(sorted(x)))
print("\nQuantidade de Números Consecutivos em Cada Sorteio:")
print(consecutivos)

# 5. Distribuição por Faixa (1-5, 6-10, 11-15, etc.)
faixas = [1, 6, 11, 16, 21, 26]  # Definindo as faixas de números
faixa_counts = {f'{faixas[i]}-{faixas[i+1]-1}': 0 for i in range(len(faixas)-1)}

for numeros in df['numeros']:
    for num in numeros:
        for i in range(len(faixas)-1):
            if faixas[i] <= num < faixas[i+1]:
                faixa_counts[f'{faixas[i]}-{faixas[i+1]-1}'] += 1

print("\nDistribuição por Faixa:")
print(faixa_counts)

# 6. Análise de Somas
df['soma_numeros'] = df['numeros'].apply(sum)
print("\nSomas dos Números Sorteados em Cada Concurso:")
print(df[['concurso', 'soma_numeros']])

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

# Exemplo de sequência a ser verificada
sequencia_a_verificar = [14, 13, 21, 19, 24, 23,  1, 17, 12,  5, 20, 17, 22,  7,  3]

# Verificar se a sequência já foi sorteada
if verificar_sequencia(sequencia_a_verificar):
    print("Essa sequência já foi sorteada.")
else:
    print("Essa sequência nunca foi sorteada.")

# 8 Decision tree

# 8.1 Criando as features e as variáveis de saída (targets)
# Vamos usar os 14 primeiros números para prever os 15 números sorteados.
X = df['numeros'].apply(lambda x: x[:]).tolist()  # Primeiros 14 números como entrada (features)
y = df['numeros'].apply(lambda x: x).tolist()       # Todos os 15 números como saída (target)

X = np.array(X)  # Converte a lista de listas de números para um array numpy
y = np.array(y)  # Converte os targets para um array numpy

# 3. Dividindo os dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Treinando um modelo para cada número (15 números)
models = []
for i in range(15):
    clf = DecisionTreeClassifier()
    clf.fit(X_train, y_train[:, i])  # Treinando para cada número individualmente
    models.append(clf)

# 5. Fazendo previsões para cada número
y_pred = np.array([model.predict(X_test) for model in models]).T  # Transposta para ter as previsões corretas

# 6. Avaliando a performance do modelo (calculando a precisão para cada número)
accuracies = []
for i in range(15):
    accuracy = accuracy_score(y_test[:, i], y_pred[:, i])
    accuracies.append(accuracy)
    #print(f'Accuracy for numero_{i+1}: {accuracy:.2f}')

# 7. Prevendo os 15 números para o próximo sorteio (usando os primeiros 14 números do último sorteio)
ultimo_sorteio = df['numeros'].iloc[-1][:]  # Últimos 14 números
previsao = np.array([model.predict([ultimo_sorteio])[0] for model in models])

print("\nPrevisão para o próximo sorteio:")
print(f"Próximos 15 números previstos: {sorted(previsao)}")
#i = 0
#for model in models:
    #i = i + 1
    #fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(20,20))
    #class_array = [str(i) for i in model.classes_]
    #print(class_array)
    #tree.plot_tree(model, class_names=class_array, filled=True)
    #file = f'arvore_loto{i+1}.png'
    #print(file)
    #fig.savefig(file)
    #plt.show()