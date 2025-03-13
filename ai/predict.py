import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suprime logs do TensorFlow
import numpy as np
import sys
from keras.src.saving import load_model

# Verifique se os parâmetros foram passados
if len(sys.argv) != 2:
    print("Uso correto: python predict.py '10,20,30,...,16'")
    sys.exit(1)

# Carregar o modelo treinado
model = load_model('C:\\git\\lotomachine\\ai\\model.h5')  # Ajuste o caminho conforme necessário

# Função para preprocessar os dados de entrada
def preprocess_input(input_str):
    # Converte a entrada em uma lista de números
    input_data = np.array([int(x) for x in input_str.split(',')])

    # Certifique-se de que o número de características seja 15
    if input_data.shape[0] != 15:
        raise ValueError("A entrada deve conter 15 características!")

    # Retorna a entrada com a forma (1, 15)
    return input_data.reshape(1, -1)


# Função para interpretar a previsão
def process_prediction(prediction):
    # Aplicar um limiar para decidir se o número é 1 ou 0
    threshold = 0.5
    predicted_numbers = (prediction > threshold).astype(int)  # 1 ou 0 baseado no limiar

    # Exibindo os números previstos
    return predicted_numbers

# Obter os dados de entrada via linha de comando
input_str = sys.argv[1]  # Exemplo: "10, 20, 30, ..., 16"

# Converter a string em uma lista de inteiros
input_numbers = np.array([int(n) for n in input_str.split(",")]).reshape(1, -1)

# Preprocessar os dados
# input_data = preprocess_input(input_str)

# Fazer a previsão
prediction = model.predict(input_numbers, verbose=0)

# Processar a previsão para obter os números inteiros
#predicted_numbers = process_prediction(prediction)

# Converter para números inteiros (exemplo: pegando os 15 maiores valores)
predicted_numbers = np.argsort(prediction[0])[-15:] + 1

# Exibir a previsão
#print("Previsão:", predicted_numbers)
print(",".join(map(str, predicted_numbers)))