import json
from utils import read_data_set

df = read_data_set()
todos_os_numeros = [num for sublist in df['numeros'] for num in sublist]
numeros_pares = [num for num in todos_os_numeros if num % 2 == 0]
numeros_impares = [num for num in todos_os_numeros if num % 2 != 0]
pares_impares = {'pares': len(numeros_pares), 'impares': len(numeros_impares)}
print(json.dumps(pares_impares))
