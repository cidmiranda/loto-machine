import random
import sys

import numpy as np

from utils import read_data_set, faixas, completar_lista, frequencias, somas
previsao_numeros_lista = []
if len(sys.argv) == 2:
    previsao_numeros_lista = np.array([int(n) for n in sys.argv[1].split(",")]).reshape(1, -1)

df = read_data_set()
# Converte faixa para proporções
list1 = [1, 2, 3, 4, 5]
total_faixas = sum(faixas().values())
# proporcao_faixas = {k: v / total_faixas for k, v in faixas().items()}
proporcao_faixas = {k: v*random.choice(list1) / total_faixas for k, v in faixas().items()}
#print(f"proporcao_faixas: {proporcao_faixas}")
media_somas = np.mean(somas())
if len(previsao_numeros_lista) > 0:
    nova_lista = completar_lista(previsao_numeros_lista[0], frequencias(), faixas(), proporcao_faixas, media_somas)
else:
    nova_lista = completar_lista(previsao_numeros_lista, frequencias(), faixas(), proporcao_faixas, media_somas)
print(sorted(nova_lista))