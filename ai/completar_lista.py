import random

from lotofacil.utils import obter_faixa


def completar_lista(previsao_numeros_lista, frequencia_numeros, faixa_numeros, proporcao_faixas, media_somas,
                    tamanho=15):

    # Se a lista estiver vazia, inicia com os números mais frequentes

    if len(previsao_numeros_lista) < 1:
        previsao_numeros_lista = random.sample(sorted(frequencia_numeros.keys(), key=lambda x: -frequencia_numeros[x]),
                                               tamanho)
    print(f"previsao_numeros_lista: {previsao_numeros_lista}")
    # Remove duplicatas mantendo a ordem
    previsao_sem_repetidos = list(dict.fromkeys(previsao_numeros_lista))
    print(f"previsao_sem_repetidos: {previsao_sem_repetidos}")
    # Se já tiver 15 números, retorna
    if len(previsao_sem_repetidos) >= tamanho:
        return previsao_sem_repetidos[:tamanho]

    # Criar uma lista ordenada pelos mais frequentes
    numeros_disponiveis = sorted(frequencia_numeros.keys(), key=lambda x: -frequencia_numeros[x])
    print(f"numeros_disponiveis: {numeros_disponiveis}")
    # Preenchendo mantendo distribuição par/ímpar
    num_pares = sum(1 for n in previsao_sem_repetidos if n % 2 == 0)
    num_impares = sum(1 for n in previsao_sem_repetidos if n % 2 != 0)
    print(f"num_pares: {num_pares}")
    print(f"num_impares: {num_impares}")
    # Conta distribuição por faixa
    distribuicao_faixa = {k: 0 for k in faixa_numeros.keys()}
    for num in previsao_sem_repetidos:
        distribuicao_faixa[obter_faixa(num)] += 1

    print(f"distribuicao_faixa: {distribuicao_faixa}")
    while len(previsao_sem_repetidos) < tamanho:
        for num in numeros_disponiveis:
            if num not in previsao_sem_repetidos:
                faixa = obter_faixa(num)
                print(f"faixa: {faixa}")
                # Mantém o equilíbrio de pares/ímpares
                #if (num % 2 == 0 and num_pares < num_impares) or (num % 2 != 0 and num_impares < num_pares):
                #    previsao_sem_repetidos.append(num)
                #    if num % 2 == 0:
                #        num_pares += 1
                #    else:
                #        num_impares += 1

                # Verifica se está dentro da proporção histórica
                print(f"distribuicao_faixa[faixa]: {distribuicao_faixa[faixa]}")
                print(f"round(proporcao_faixas[faixa] * tamanho): {round(proporcao_faixas[faixa] * tamanho)}")
                if distribuicao_faixa[faixa] < round(proporcao_faixas[faixa] * tamanho):
                    print(f"num: {num}")
                    print(f"num_pares: {num_pares}")
                    print(f"num_impares: {num_impares}")
                    if (num % 2 == 0 and num_pares < num_impares) or (num % 2 != 0 and num_impares <= num_pares):
                        previsao_sem_repetidos.append(num)
                        distribuicao_faixa[faixa] += 1
                        if num % 2 == 0:
                            num_pares += 1
                        else:
                            num_impares += 1
                # Se a soma estourar a média histórica, para
                if sum(previsao_sem_repetidos) > media_somas + 10:
                    break

            if len(previsao_sem_repetidos) >= tamanho:
                break

    return previsao_sem_repetidos[:tamanho]