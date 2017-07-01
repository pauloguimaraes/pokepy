# -*- coding: UTF-8 -*-
# pylint: disable=C0103,C0111,C0301

#
# Exercício de Progamação Processamento - Computação Gráfica
# Universidade de São Paulo
# Escola de Artes, Ciências e Humanidades
# Graduação em Sistemas de Informação
# Professor João Bernardes
#
# Gabriel Ueti Amaro                  9922057
# Paulo Henrique Freitas Guimarães    9390361
# Silas Fernandes Moreira             9761718
# Tiago de Luna Farias                9875503
# William de Souza Almeida            9377567
#

from PIL import Image
import cv2 as ocv

# Recuperando o nome da imagem para criar um folder com as
# imagens de saída
FOLDER = ''
def set_folder(caminho_arquivo):
    global FOLDER
    FOLDER = str.split(caminho_arquivo, '/')
    FOLDER = str.split(FOLDER[len(FOLDER)-1], '.')[0]
    FOLDER = './{}'.format(FOLDER)

# Método responsável por cortar a imagem inicialmente
# Despreza 15% das laterais e 30% dos extremos
def cortar(caminho_arquivo):
    import os
    imagem = Image.open(caminho_arquivo)

    width, height = imagem.size[0], imagem.size[1]
    x_desprezivel = width / 20
    y_desprezivel = height / 10

    quadro_a_cortar = (
        x_desprezivel * 3,
        y_desprezivel * 3,
        x_desprezivel * 17,
        y_desprezivel * 7
    )

    imagem = imagem.crop(quadro_a_cortar)

    # Cria o folder para as imagens de output
    set_folder(caminho_arquivo)
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    imagem.save('{}/1_corte.png'.format(FOLDER))

    return imagem


# Aplica filtro de Vignette
# Basicamente reduz o brilho ou saturação na periferia da imagem comparando-se ao centro
#
# Referência: https://stackoverflow.com/questions/22654770/creating-vignette-filter-in-opencv
def aplica_vignette(caminho_arquivo):
    img = ocv.imread(caminho_arquivo)
    rows, cols, channel = img.shape
    # Monta dois kernels para linhas e colunas, respectivamente
    kernel_x = ocv.getGaussianKernel(cols, 100)
    kernel_y = ocv.getGaussianKernel(rows, 100)
    # Multiplica o kernel das linhas pela transposta do kernel das colunas
    kernel = kernel_x.T * kernel_y
    # Cria a máscara
    mask = kernel / kernel.max()
    output = img

    # Aplica a máscara na imagem
    for i in range(3):
        output[:, :, i] = output[:, :, i] * mask

    ocv.imwrite('{}/2_vignette.png'.format(FOLDER), output)
    return output


# Método responsável por reforçar os pontos mais iluminados na imagem
# Converte a imagem para LAB (Lightnes, Green-Red, Blue-Yellow)
#
# Referência: https://stackoverflow.com/questions/24341114/simple-illumination-correction-in-images-opencv-c
def processa_iluminacao(caminho_arquivo):
    imagem = ocv.imread(caminho_arquivo)

    # Converte de RGB para LAB
    lab = ocv.cvtColor(imagem, ocv.COLOR_RGB2LAB)
    # Separa os canais
    l, a, b = ocv.split(lab)
    clahe = ocv.createCLAHE(clipLimit=1.0, tileGridSize=(8, 8))
    # Reaplica o canal L
    cl = clahe.apply(l)
    # Mescla novamente os canais
    limg = ocv.merge((cl, a, b))
    ocv.imwrite('{}/3_clahe.png'.format(FOLDER), limg)

    # Recolore para RGB
    final = ocv.cvtColor(limg, ocv.COLOR_LAB2RGB)
    ocv.imwrite('{}/4_iluminada.png'.format(FOLDER), final)

    return imagem


# Converte a imagem para escala de cinza
# Aplica um filtro Gaussiano
# Aplica threshold de forma decrescente até que 10% da imagem seja branca
def identifica_pontos_iluminados(caminho_arquivo):
    imagem = ocv.imread(caminho_arquivo)

    # Converte para escala de cinza
    gray = ocv.cvtColor(imagem, ocv.COLOR_RGB2GRAY)
    ocv.imwrite('{}/5_cinza.png'.format(FOLDER), gray)

    # Aplica um filtro gaussiano
    blurred = ocv.GaussianBlur(gray, (11, 11), 0)
    ocv.imwrite('{}/6_blurred.png'.format(FOLDER), blurred)

    # Aplica um threshold de 254
    base = 254
    thresh = ocv.threshold(blurred, base, 255, ocv.THRESH_BINARY)[1]

    # Proporciona pixels pretos e brancos
    p_b, p_p = conta_pixels_brancos_e_pretos(thresh)

    # Repete a operação até 10% da imagem estar branca
    comparativo = 10
    while ((p_b < comparativo and p_p > 100 - comparativo) or (p_p < comparativo and p_b < 100 - comparativo)) and base >= 1:
        base -= 1
        thresh = ocv.threshold(blurred, base, 255, ocv.THRESH_BINARY)[1]
        p_b, p_p = conta_pixels_brancos_e_pretos(thresh)

    # Aplica abertura e fechamento
    thresh = ocv.erode(thresh, None, iterations=2)
    thresh = ocv.dilate(thresh, None, iterations=4)
    ocv.imwrite('{}/7_threshold.png'.format(FOLDER), thresh)

    return thresh


# Remove labels muito pequenos da imagem já mascarada
# Removendo sujeira
#
# Referência: http://www.pyimagesearch.com/2016/10/31/detecting-multiple-bright-spots-in-an-image-with-python-and-opencv/
def remove_labels_pequenos(caminho_arquivo):
    from skimage import measure
    import numpy as np

    img = ocv.imread(caminho_arquivo, ocv.COLOR_BGR2GRAY)

    labels = measure.label(img, neighbors=8, background=0)
    mask = np.zeros(img.shape, dtype='uint8')

    for label in np.unique(labels):
        if label == 0:
            continue

        label_mask = np.zeros(img.shape, dtype='uint8')
        label_mask[labels == label] = 255
        num_pixels = ocv.countNonZero(label_mask)
        # Considera componentes com menos de 300 pixels desprezíveis
        if num_pixels > 300:
            mask = ocv.add(mask, label_mask)

    ocv.imwrite('{}/8_semlabels.png'.format(FOLDER), mask)

    return mask


# Aplica operação E entre imagem original e sem labels
# Faz com que os pixels brancos passem a receber a cor do pixel original
def operacao_e(caminho_arquivo_mascara, caminho_arquivo_original):
    img = ocv.imread(caminho_arquivo_mascara, ocv.COLOR_BGR2GRAY)
    original = ocv.imread(caminho_arquivo_original)
    colorida = ocv.cvtColor(img, ocv.COLOR_GRAY2BGR)

    # Percorre a imagem em escala de cinza
    # Pinta os pixels brancos com seus equivalentes na imagem colorida
    height, width = img.shape
    for x in range(0, width):
        for y in range(0, height):
            if img[y][x] != 0:
                colorida[y][x] = original[y][x]

    ocv.imwrite('{}/9_operacaoe.png'.format(FOLDER), colorida)

    return colorida


# Normaliza a coloração da imagem
# Usa uma biblioteca CSS que mapeia as cores conhecidas (black, lightgreen, cyan, etc.)
# Troca a cor do pixel atual pela conhecida mais próxima
def normaliza_cores(caminho_arquivo):
    img = ocv.imread(caminho_arquivo)

    # Percorre a imagem e normaliza pixels coloridos
    width, height, channel = img.shape
    for x in range(0, width):
        for y in range(0, height):
            img[x][y] = cor_proxima(tuple(img[x][y]))

    ocv.imwrite('{}/10_normalizada.png'.format(FOLDER), img)
    return img


# Limpa os pixels acima da metade da imagem
def limpa_cores_isoladas_no_topo(caminho_arquivo):
    img = ocv.imread(caminho_arquivo)

    height, width, channel = img.shape
    topo = 0

    # Encontra a última linha toda preta
    for y in range(0, height / 2):
        deve_considerar = True
        for x in range(0, width):
            if img[y][x][0] != 0 or img[y][x][1] != 0 or img[y][x][2] != 0:
                deve_considerar = False
                break

        if deve_considerar:
            topo = y

    # Pinta tudo de preto até a última linha encontrada
    for y in range(0, topo):
        for x in range(0, width):
            img[y][x] = [0, 0, 0]

    ocv.imwrite('{}/11_limpa.png'.format(FOLDER), img)
    return img


# Conta os pixels pretos e brancos na imagem passada como parâmetro
def conta_pixels_brancos_e_pretos(imagem):
    width, height = imagem.shape
    n_b, n_p = 0, 0

    for x in range(0, width):
        for y in range(0, height):
            if imagem[x][y] == 0:
                n_p += 1
            else:
                n_b += 1

    total = n_p + n_b
    p_b = (n_b * 100.0) / total
    p_p = (n_p * 100.0) / total
    return p_b, p_p


# Usa a biblioteca WebColors
# Calcula a cor conhecida mais próxima da tupla RGB passada como parâmetro
#
# Referência: https://stackoverflow.com/questions/9694165/convert-rgb-color-to-english-color-name-like-green
def cor_proxima(rgb):
    import webcolors

    if rgb[0] == rgb[1] == rgb[2] == 0:
        return webcolors.name_to_rgb('black')

    min_colours = {}
    for pokemon, nome in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(pokemon)
        r_d = (r_c - rgb[0]) ** 2
        g_d = (g_c - rgb[1]) ** 2
        b_d = (b_c - rgb[2]) ** 2
        min_colours[(r_d + g_d + b_d)] = nome

    res = webcolors.name_to_rgb(min_colours[min(min_colours.keys())])
    return res


# Cria um mapa da imagem
# <Cor, Quantidade de Pixels>
# Despreza cores com baixa taxa de ocorrência
def monta_conjunto(caminho_arquivo):
    imagem = ocv.imread(caminho_arquivo)

    vetor_cores = []
    height, width, shape = imagem.shape

    # Monta uma lista de cores presentes na imagem
    for y in range(0, height):
        for x in range(0, width):
            cor = imagem[y][x]
            if cor[0] != 0 or cor[1] != 0 or cor[2] != 0:
                vetor_cores.append(tuple(cor))

    # Transforma a lista em conjunto
    conjunto_ref = set(vetor_cores)

    # Prepara um dicionário que relaciona a cor presente no conjunto
    # com o número de ocorrências da mesma na lista
    dicionario = dict()
    for elemento in conjunto_ref:
        dicionario[elemento] = vetor_cores.count(elemento)

    # Conta o total de ocorrências
    total_ocorrencias = 0
    for cor, ocorrencia in dicionario.items():
        total_ocorrencias += ocorrencia

    # Desprezando cores com baixa ocorrência
    irrelevante = (total_ocorrencias * 0.5) / 100.0
    for cor, ocorrencia in dicionario.items():
        if ocorrencia < irrelevante:
            del dicionario[cor]

    return dicionario


# Repassa a chamada para o DAO
def grava_na_base(pokemon_name, dicionario_ocorrencia):
    from dao import insere_cor
    insere_cor(pokemon_name, dicionario_ocorrencia)


# Processa o resultado da busca na base
def busca(dicionario_ocorrencia):
    from ast import literal_eval as make_tuple
    from dao import get

    resultado = get(dicionario_ocorrencia)

    # Salva resultado em um mapa
    # <Pokemon, <Cor, Ocorrência>>
    ocorr_bd = dict()
    for linha in resultado:
        pokename = str(linha[2])
        cor = make_tuple(linha[0])

        if pokename not in ocorr_bd:
            ocorr_bd[pokename] = dict()

        ocorr_bd[pokename][cor] = linha[1]

    # Calcula o número de pixels coloridos em cada Pokemon
    total_pokes = dict()
    for pokemon, mapa_cor in ocorr_bd.items():
        for cor, ocorrencia in mapa_cor.items():
            if pokemon not in total_pokes:
                total_pokes[pokemon] = 0
            total_pokes[pokemon] += ocorrencia

    # Transforma os valores descobertos para porcentagem
    for pokemon, mapa_cor in ocorr_bd.items():
        for cor, ocorrencia in mapa_cor.items():
            ocorr_bd[pokemon][cor] = (ocorrencia * 100.0) / total_pokes[pokemon]

    # Calcula o número de pixels coloridos no mapa passado como parâmetro
    total_pixels = 0
    for pokemon, mapa_cor in dicionario_ocorrencia.items():
        total_pixels += mapa_cor

    # Transforma os valores descobertos para porcentagem
    for pokemon, mapa_cor in dicionario_ocorrencia.items():
        dicionario_ocorrencia[pokemon] = (dicionario_ocorrencia[pokemon] * 100.0) / total_pixels

    # Faz o cálculo de diferenças entre a imagem que vem como parâmetro e cada um dos Pokemons
    # Diferença = Somatória do Módulo da porcentagem de ocorrência no Pokemon subtraído da porcentagem de ocorrência no mapa analisado para cada uma das cores
    possibilidade_de_ser = dict()
    cores_nao_presentes = dict()
    for pokemon, mapa_cor in ocorr_bd.items():
        cores_nao_presentes[pokemon] = mapa_cor
        if pokemon not in possibilidade_de_ser:
            possibilidade_de_ser[pokemon] = 0

        for cor, ocorrencia in mapa_cor.items():
            if cor not in dicionario_ocorrencia:
                possibilidade_de_ser[pokemon] += ocorrencia
            else:
                possibilidade_de_ser[pokemon] += abs(ocorrencia - dicionario_ocorrencia[cor])
                # Remove tal cor das não presentes
                cores_nao_presentes[pokemon][cor] = 0

    # Soma-se as cores não presentes na diferença
    for pokemon, mapa_cor in cores_nao_presentes.items():
        for cor, ocorrencia in mapa_cor.items():
            possibilidade_de_ser[pokemon] += ocorrencia

    # Indica o tamanho da linha a analisar
    soma_total = 0
    for pokemon, mapa_cor in possibilidade_de_ser.items():
        soma_total += mapa_cor

    # Decide qual o que possui a maior ocorrência
    i = 0
    valor = 0
    maior = 'pikachu'
    for pokemon, mapa_cor in possibilidade_de_ser.items():

        iteracao = (((soma_total - mapa_cor) * 100.0) / soma_total)
        if i == 0:
            valor = iteracao
            maior = pokemon
        else:
            if iteracao > valor:
                valor = iteracao
                maior = pokemon
        i += 1

    print 'Existe {}% de compatibilidade com o {}'.format(valor, str(maior))
