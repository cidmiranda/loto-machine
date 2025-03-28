import pandas as pd
from utils import read_data_set

df = read_data_set()

todos_os_numeros = [num for sublist in df['numeros'] for num in sublist]

frequencia_numeros = pd.Series(todos_os_numeros).value_counts().sort_values(ascending=False)

#Probabilidade de Sorteio de Cada Número (teórica)
total_sorteios = len(df)
probabilidades = frequencia_numeros / total_sorteios
print(probabilidades.head(25))