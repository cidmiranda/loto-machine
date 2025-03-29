import json
from utils import contar_consecutivos, read_data_set

df = read_data_set()
df['consecutivos'] = df['numeros'].apply(lambda x: contar_consecutivos(sorted(x)))
# consecutivos = df['numeros'].apply(lambda x: contar_consecutivos(sorted(x)))
consecutivos = df[['concurso', 'consecutivos']].to_dict(orient='records')
print(json.dumps(consecutivos))