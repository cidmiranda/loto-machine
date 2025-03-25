import ccxt
import numpy as np
import pandas as pd
from keras import Sequential
from keras.src.layers import LSTM, Dropout, Dense
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

exchange = ccxt.binance()

# Função para buscar os dados do mercado (OHLCV)
def fetch_data(symbol_fetch, timeframe_fetch, limit):
    ohlcv = exchange.fetch_ohlcv(symbol_fetch, timeframe_fetch, limit=limit)
    df_fetch = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_fetch['timestamp'] = pd.to_datetime(df_fetch['timestamp'], unit='ms')
    return df_fetch

symbol = 'AUCTION/USDT'
timeframe = '5m'  # Velas diárias

# Baixar os últimos 500 candles
#ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=500)
#df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df = fetch_data(symbol, timeframe, limit=5000)

# Visualizando os primeiros dados
print(df.head())

# Usando apenas o preço de fechamento
data = df[['timestamp', 'close']]

# Normalizando os dados
scaler = MinMaxScaler(feature_range=(0, 1))
data['close'] = scaler.fit_transform(data['close'].values.reshape(-1, 1))

# Criar sequências para treinamento
def create_sequences(data, seq_length):
    X = []
    y = []
    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        # Definindo target: 1 se o próximo valor for maior, 0 se for menor
        y.append(1 if data[i + seq_length] > data[i + seq_length - 1] else 0)
    return np.array(X), np.array(y)

seq_length = 50  # Usar as últimas 50 horas para prever a próxima
X, y = create_sequences(data['close'].values, seq_length)

# Dividir os dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Reshape para [samples, time steps, features]
X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# Exibindo as dimensões
print(f"X_train shape: {X_train.shape}")
print(f"X_test shape: {X_test.shape}")

# Construção do modelo LSTM para Classificação
model = Sequential()

# Adicionar a primeira camada LSTM com Dropout
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(Dropout(0.2))

# Adicionar a segunda camada LSTM
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))

# Camada de saída (usando 'sigmoid' para classificação binária)
model.add(Dense(units=1, activation='sigmoid'))

# Compilação do modelo
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Resumo do modelo
model.summary()

# Treinamento do modelo
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

# Previsão e avaliação
y_pred = model.predict(X_test)
y_pred = (y_pred > 0.5).astype(int)  # Convertendo probabilidades para 0 ou 1

# Avaliar a performance
from sklearn.metrics import accuracy_score, classification_report
accuracy = accuracy_score(y_test, y_pred)
print(f'Acurácia do modelo: {accuracy:.2f}')
print(classification_report(y_test, y_pred))

# Visualização do resultado
import matplotlib.pyplot as plt

plt.plot(y_test, color='red', label='Tendência Real')
plt.plot(y_pred, color='blue', label='Tendência Prevista')
plt.title('Previsão de Tendência com LSTM')
plt.xlabel('Hora')
plt.ylabel('Tendência (0 = Baixa, 1 = Alta)')
plt.legend()
plt.show()