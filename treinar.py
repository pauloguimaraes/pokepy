# -*- coding: UTF-8 -*-
# pylint:disable=C0103,C0111

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

import sys
from processar import cortar, aplica_vignette, processa_iluminacao
from processar import identifica_pontos_iluminados, remove_labels_pequenos
from processar import operacao_e, normaliza_cores, limpa_cores_isoladas_no_topo
from processar import monta_conjunto, grava_na_base

def run(nome_pokemon, nome_imagem):
    folder = str.split(nome_imagem, '/')
    folder = str.split(folder[len(folder)-1], '.')[0]
    folder = './{}'.format(folder)

    # ETAPA 1: Cortar a imagem
    cortar(
        caminho_arquivo=nome_imagem
    )

    # ETAPA 2: Aplicar o filtro Vignette
    aplica_vignette(
        caminho_arquivo='{}/1_corte.png'.format(folder)
    )

    # ETAPA 3: Reforça os locais iluminados
    processa_iluminacao(
        caminho_arquivo='{}/2_vignette.png'.format(folder)
    )

    # ETAPA 4: Deixa os campos iluminados brancos e o restante preto
    identifica_pontos_iluminados(
        caminho_arquivo='{}/4_iluminada.png'.format(folder)
    )

    # ETAPA 5: Remove pequenos campos brancos
    remove_labels_pequenos(
        caminho_arquivo='{}/7_threshold.png'.format(folder)
    )

    # ETAPA 6: Pinta os campos em branco com as cores da imagem original
    operacao_e(
        caminho_arquivo_mascara='{}/8_semlabels.png'.format(folder),
        caminho_arquivo_original='{}/1_corte.png'.format(folder)
    )

    # ETAPA 6: Normaliza as cores
    normaliza_cores(
        caminho_arquivo='{}/9_operacaoe.png'.format(folder)
    )

    # ETAPA 7: Limpa campos isolados por linhas pretas
    limpa_cores_isoladas_no_topo(
        caminho_arquivo='{}/10_normalizada.png'.format(folder)
    )

    rgb = monta_conjunto(
        caminho_arquivo='{}/11_limpa.png'.format(folder)
    )

    grava_na_base(
        pokemon_name=nome_pokemon,
        dicionario_ocorrencia=rgb
    )

if __name__ == "__main__":
    imagem = sys.argv[1]
    poke = sys.argv[2]
    run(poke, imagem)
    