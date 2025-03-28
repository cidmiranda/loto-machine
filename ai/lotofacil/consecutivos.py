from utils import contar_consecutivos, read_data_set

df = read_data_set()
consecutivos = df['numeros'].apply(lambda x: contar_consecutivos(sorted(x)))
print(consecutivos)