import array

import pandas as pd
from pymongo import MongoClient
import json
from types import SimpleNamespace

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["lotofacil"]
collection = db["resultados"]

# Buscar todos os documentos do MongoDB
dados = list(collection.find({}, {"_id": 0}))  # Exclui o campo _id

jsonDataSetArray = []
for dado in dados:
    dumpDado = json.dumps(dado)
    loadDado = json.loads(dumpDado, object_hook=lambda d: SimpleNamespace(**d))
    desired_array = [int(numeric_string) for numeric_string in loadDado.numeros]
    jsonDataSet = {'concurso': loadDado.concurso,
                   'data': loadDado.data,
                   'num0':desired_array[0],
                   'num1':desired_array[1],
                   'num2':desired_array[2],
                   'num3':desired_array[3],
                   'num4':desired_array[4],
                   'num5':desired_array[5],
                   'num6':desired_array[6],
                   'num7':desired_array[7],
                   'num8':desired_array[8],
                   'num9':desired_array[9],
                   'num10':desired_array[10],
                   'num11':desired_array[11],
                   'num12':desired_array[12],
                   'num13':desired_array[13],
                   'num14':desired_array[14]
                   }
    jsonDataSetArray.append(jsonDataSet)

# Criar um DataFrame pandas
df = pd.DataFrame(jsonDataSetArray)

# Exportar para CSV
df.to_csv("dataset/lotofacil_historico.csv", index=False)
print("Arquivo CSV gerado com sucesso!")