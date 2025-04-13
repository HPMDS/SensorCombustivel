from random import choice,seed



seed(4)
caracteres='0123456789ABCDEF'




def gera_random(tamanho):
    return ''.join(choice(caracteres) for _ in range(tamanho))