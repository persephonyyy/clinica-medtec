def ordenar_por_nome(lista):
    resultado = list(lista) 

    for i in range(1, len(resultado)):
        atual = resultado[i]
        j = i - 1

        while j >= 0 and resultado[j]["nome"].lower() > atual["nome"].lower():
            resultado[j + 1] = resultado[j]
            j -= 1

        resultado[j + 1] = atual  

    return resultado


def buscar_por_nome(lista, termo):
    termo = termo.lower().strip()
    encontrados = []

    for item in lista:
        if termo in item["nome"].lower():
            encontrados.append(item)

    return encontrados