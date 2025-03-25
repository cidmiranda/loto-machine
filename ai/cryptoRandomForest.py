import ccxt
import talib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler

exchange = ccxt.binance()

# Buscar dados de velas (OHLCV) para o par BTC/USDT no timeframe de 1 hora
def fetch_data(symbol_, timeframe_, limit):
    ohlcv = exchange.fetch_ohlcv(symbol_, timeframe_, limit=limit)
    df_ = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_['timestamp'] = pd.to_datetime(df_['timestamp'], unit='ms')
    return df_

symbol = 'AUCTION/USDT'
timeframe = '5m'  # Velas diárias

df = fetch_data(symbol, timeframe, limit=500)

# Criar a variável target (1 = preço sobe, 0 = preço cai)
df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

# Indicadores técnicos
df['ma14'] = talib.SMA(df['close'], timeperiod=14)
df['rsi'] = talib.RSI(df['close'], timeperiod=14)
df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
df['roc'] = talib.ROC(df['close'], timeperiod=10)

# Bollinger Bands
df['upperband'], df['middleband'], df['lowerband'] = talib.BBANDS(df['close'], timeperiod=20)

# Índice Direcional Médio (ADX)
df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)

# Stochastic Oscillator
df['slowk'], df['slowd'] = talib.STOCH(df['high'], df['low'], df['close'], fastk_period=14, slowk_period=3, slowd_period=3)

# Volatilidade (normalizada)
df['volatility'] = (df['high'] - df['low']) / df['close']

# Candle Patterns
df['doji'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
df['engulfing'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
df['hammer'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])

# Criar lags (valores passados)
for lag in range(1, 4):
    df[f'close_lag{lag}'] = df['close'].shift(lag)
    df[f'volume_lag{lag}'] = df['volume'].shift(lag)

# Remover NaN
df.dropna(inplace=True)

# Selecionar features para o modelo
features = ['open', 'high', 'low', 'close', 'volume', 'ma14', 'rsi', 'macd', 'atr', 'roc',
            'upperband', 'middleband', 'lowerband', 'adx', 'slowk', 'slowd', 'volatility',
            'doji', 'engulfing', 'hammer', 'close_lag1', 'close_lag2', 'close_lag3',
            'volume_lag1', 'volume_lag2', 'volume_lag3']

X = df[features]
y = df['target']

# Normalizar os dados
scaler = StandardScaler()
X = pd.DataFrame(scaler.fit_transform(X), columns=features)

# Dividir em treino (80%) e teste (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Definir os hiperparâmetros a serem testados

param_grid = {
    'n_estimators': [100, 200, 300], # Número de árvores
    'max_depth': [5, 10, 20],        # Profundidade máxima
    'min_samples_split': [2, 5, 10], # Mínimo de amostras para dividir um nó
    'min_samples_leaf': [1, 3, 5],   # Mínimo de amostras em um nó folha
    'max_features': ['sqrt', 'log2', None],
    'bootstrap': [True, False]  # Se usa amostragem com reposição
}

# Usar RandomizedSearchCV (mais rápido que GridSearchCV)
rf = RandomForestClassifier(random_state=42)
random_search = RandomizedSearchCV(rf, param_grid, n_iter=10, cv=3, n_jobs=-1, verbose=1)
random_search.fit(X_train, y_train)

# Melhor modelo encontrado
best_model = random_search.best_estimator_

# Avaliar o modelo
y_pred = best_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f'Melhor acurácia do modelo otimizado: {accuracy:.2f}')
print(f'Melhores parâmetros: {random_search.best_params_}')

# 🔥 **Usar o último candle para obter o preço atual**
last_data = df.iloc[-1:][features]
current_price = df.iloc[-1]['close']  # Pegando o preço de fechamento do último candle

# 🔥 **Fazer previsão usando os dados mais recentes**
predicted_trend = best_model.predict(last_data)[0]

if predicted_trend == 1:
    print(f"Tendência de ALTA detectada! Último preço fechado: ${current_price:.2f}")
else:
    print(f"Tendência de BAIXA detectada! Último preço fechado: ${current_price:.2f}")