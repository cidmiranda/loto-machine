import sys

import numpy as np

from utils import read_data_set, numeros_sorteados_concurso

# Verificar se os parâmetros foram passados
if len(sys.argv) != 3:
    print("Uso correto: python predict.py '10,20,30,...,16'")
    sys.exit(1)

df = read_data_set()
# Obter os dados de entrada via linha de comando
input_numbers = np.array([int(n) for n in sys.argv[1].split(",")]).reshape(1, -1)

# Converter a string em uma lista de inteiros
sequencia_a_verificar = input_numbers[0]
concurso_a_verificar = sys.argv[2]  # Número do concurso a comparar
numeros_acertados = numeros_sorteados_concurso(df, concurso_a_verificar, sequencia_a_verificar)
print(numeros_acertados)
