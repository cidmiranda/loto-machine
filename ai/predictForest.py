import sys
import numpy as np
import pickle
import pandas as pd

# Verificar se os argumentos foram passados
if len(sys.argv) < 2 or sys.argv[1] == '':
    print("Erro: Por favor, forneça os números sorteados como entrada.")
    sys.exit(1)

# Tentar dividir os números e convertê-los para inteiros
try:
    input_data = np.array([int(x) for x in sys.argv[1].split(",")])
except ValueError:
    print("Erro: Certifique-se de que todos os números fornecidos sejam inteiros.")
    sys.exit(1)

# Carregar o modelo treinado a partir do arquivo .pkl
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# AQUI: Nomes das colunas do seu modelo durante o treinamento (ajuste conforme necessário)
# As colunas devem ser as mesmas usadas no treinamento
column_names = ['num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7', 'num8', 'num9', 'num10', 'num11', 'num12', 'num13']


# Obter os números passados por argumento
# input_data = np.array([int(x) for x in sys.argv[1].split(",")])
input_data_df = pd.DataFrame([input_data], columns=column_names)

# Prever a saída (ajuste conforme necessário para a forma esperada pelo seu modelo)
# prediction = model.predict(input_data.reshape(1, -1))  # Ajuste a forma dependendo do seu modelo
prediction = model.predict(input_data_df)

# Exibir a previsão
print(prediction[0])  # Exibe o resultado da previsão