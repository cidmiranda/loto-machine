import pandas as pd
import numpy as np
from keras import Sequential
from keras.src.layers import Dense, Reshape
from keras.src.optimizers import Adam
from keras.src.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from lotofacil import convert_to_int

# Carregar os dados do arquivo CSV
df = pd.read_csv('dataset/lotofacil_historico.csv', header=None)

# Renomear as colunas
df.columns = ['concurso', 'data'] + [f'numero_{i}' for i in range(1, 16)]

# Aplicando a conversão nas colunas de números (começando da coluna 2 até a última)
df['numeros'] = df.iloc[:, 2:].apply(lambda row: convert_to_int(row), axis=1)

# Garantir que todos os sorteios tenham 15 números
df = df[df['numeros'].apply(lambda x: len(x) == 15)]

# Criando as features e as variáveis de saída (targets)
X = df['numeros'].apply(lambda x: x[:-1]).tolist()  # Primeiros 14 números como entrada
y = df['numeros'].apply(lambda x: x).tolist()       # Todos os 15 números como saída

# Convertendo para arrays numpy
X = np.array(X)
y = np.array(y)

# Normalizando os dados
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)  # Normalizando as entradas (valores de 1 a 25)

# Dividindo os dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Convertendo as saídas para one-hot encoding (para cada um dos 15 números)
y_train_onehot = np.array([to_categorical(y_i - 1, num_classes=25) for y_i in y_train])
y_test_onehot = np.array([to_categorical(y_i - 1, num_classes=25) for y_i in y_test])

# Construindo a rede neural
model = Sequential()

# Primeira camada oculta
model.add(Dense(units=128, input_dim=14, activation='relu'))

# Segunda camada oculta
model.add(Dense(units=128, activation='relu'))

# Camada de saída com 15 neurônios, cada um representando um número sorteado
# Cada número é mapeado para uma distribuição de 25 probabilidades (para os números de 1 a 25)
model.add(Dense(units=15 * 25, activation='softmax'))  # 15 números, cada um com 25 possíveis

# Reshape para que a saída tenha a forma (None, 15, 25)
model.add(Reshape((15, 25)))

# Compilando o modelo
model.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy'])

# Treinando o modelo
model.fit(X_train, y_train_onehot, epochs=50, batch_size=32, validation_data=(X_test, y_test_onehot))

# Avaliando o modelo
loss, accuracy = model.evaluate(X_test, y_test_onehot)
print(f"Modelo avaliado - Perda: {loss:.4f}, Acurácia: {accuracy:.4f}")

# Fazendo previsões para o próximo sorteio
ultimo_sorteio = df['numeros'].iloc[-1][:-1]  # Últimos 14 números
ultimo_sorteio_scaled = scaler.transform([ultimo_sorteio])  # Normalizando os dados de entrada
previsao = model.predict(ultimo_sorteio_scaled)

# Convertendo a previsão em números inteiros
previsao_numeros = np.argmax(previsao, axis=2) + 1  # Convertendo para a faixa de 1 a 25

print("\nPrevisão para o próximo sorteio:")
print(f"Próximos 15 números previstos: {previsao_numeros}")