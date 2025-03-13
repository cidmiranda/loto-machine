import numpy as np
import pandas as pd
from keras import Sequential
from keras.src.layers import Dense
from keras.src.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

# Carregar o dataset
df = pd.read_csv("dataset/lotofacil_historico.csv")

# print(df.head)
# Assumindo que as últimas 15 colunas são os números sorteados
X = df.iloc[:, 2:-15].values  # Seleciona as colunas de números sorteados, sem as colunas extras
y = df.iloc[:, -15:].values  # Seleciona as últimas 15 colunas (os rótulos)

# Verifique os shapes de X e y
print(f"Shape de X: {X.shape}")
print(f"Shape de y: {y.shape}")

# Convertendo os números sorteados para formato binário (One-Hot Encoding)
mlb = MultiLabelBinarizer(classes=range(1, 26))  # Lotofácil tem números de 1 a 15
y_binary = mlb.fit_transform(y)


# Verifique o número de registros no seu DataFrame
print(f"Total de registros: {len(df)}")

# Veja as primeiras linhas para garantir que o DataFrame foi carregado corretamente
# print(df.head())

# Verifique a quantidade de colunas
print(f"Total de colunas: {df.shape[1]}")

# Certifique-se de que X e y não estão vazios
if X.shape[0] == 0 or y.shape[0] == 0:
    raise ValueError("Os dados de entrada ou saída estão vazios!")

# Remover colunas não numéricas de X (por exemplo, 'data' ou qualquer outra coluna não numérica)
X = df.select_dtypes(include=['number'])  # Isso seleciona apenas as colunas numéricas
X = X.drop(columns=['concurso'])  # Excluir a coluna 'concurso' se necessário

# Dividir os dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y_binary, test_size=0.2, random_state=42)

# Verifique se o split ocorreu corretamente
print(f"Shape de X_train: {X_train.shape}, X_test: {X_test.shape}")
print(f"Shape de y_train: {y_train.shape}, y_test: {y_test.shape}")

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
y_train = y_train.astype('float32')
y_test = y_test.astype('float32')

# Criando o modelo
model = Sequential()

# Primeira camada oculta com 64 neurônios e ReLU
model.add(Dense(64, input_dim=X.shape[1], activation='relu'))

# Segunda camada oculta com 32 neurônios
model.add(Dense(32, activation='relu'))

# Camada de saída com 15 neurônios e ativação sigmoide
model.add(Dense(25, activation='sigmoid'))  # 25 para 25 números

# Compilando o modelo
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Treinando o modelo
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

# Salvando o modelo
model.save("model.h5")
print("Modelo treinado e salvo!")