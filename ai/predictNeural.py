import sys
import numpy as np
from keras.src.saving import load_model

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

# Carregar o modelo treinado
model = load_model('modelo.h5')  # Ou o caminho do seu modelo .h5

# Quantidade de características esperadas pelo modelo
expected_features = model.input_shape[1]  # Obtém o número de features esperadas

# Verificar se a entrada tem o número correto de características
if input_data.shape[0] != expected_features:
    print(f"Erro: o modelo espera {expected_features} características, mas você forneceu {input_data.shape[0]}.")
    sys.exit(1)

# Ajustar formato da entrada para prever corretamente
input_data = input_data.reshape(1, -1)  # Transforma em matriz 2D para previsão

# Fazer a previsão
prediction = model.predict(input_data)

# Arredondar e converter para inteiro no intervalo de 1 a 25
predicted_number = int(round(prediction[0][0]))

# Garantir que está no intervalo esperado
predicted_number = max(1, min(25, predicted_number))

# Exibir a previsão
print(f"Previsão: {predicted_number}")