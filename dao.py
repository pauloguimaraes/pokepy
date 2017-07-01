# -*- coding: UTF8 -*-
# pylint: disable=C0111,C0301

#
# Exercício de Progamação Processamento - Computação Gráfica
# Universidade de São Paulo
# Escola de Artes, Ciências e Humanidades
# Graduação em Sistemas de Informação
# Professor João Bernardes
#
# Gabriel Ueti Amaro                  9922057
# Paulo Henrique Freitas Guimarães    9390361
# Tiago de Luna Farias                9875503
# William de Souza Almeida            9377567
#


# Conecta à base MySQL que contém o treinamento dos Pokemons
def conecta(usuario='root', senha='123456', nome_bd='pokemon_go'):
    import mysql.connector
    return mysql.connector.connect(user=usuario, password=senha, database=nome_bd)

# Insere a cor para o Pokemon passado como parâmetro
def insere_cor(pokemon_name, dicionario_ocorrencia):
    con = conecta()
    cursor = con.cursor()

    # Num primeiro momento verifica a existência na base
    query = 'SELECT COUNT(*) FROM pokemon WHERE nome = UPPER(%s);'
    dados = (pokemon_name,)

    cursor.execute(query, dados)
    total = cursor.fetchall()
    total = total[0][0]

    existe = total > 0

    if not existe:
        query = 'INSERT INTO pokemon(nome) VALUES(UPPER(%s));'
        dados = (pokemon_name,)
        cursor.execute(query, dados)

    # Depois insere suas cores
    for pokemon, mapa_cor in dicionario_ocorrencia.items():
        query = 'SELECT COUNT(*) FROM pokemon_color WHERE pokemon_id = (SELECT id FROM pokemon WHERE nome = UPPER(%s) LIMIT 1) AND rgb = %s'
        dados = (pokemon_name, str(pokemon))

        cursor.execute(query, dados)
        total = cursor.fetchall()
        total = total[0][0]

        deve_continuar = total > 0
        if deve_continuar:
            query = 'UPDATE pokemon_color SET n_ocorrencias = n_ocorrencias + %s WHERE pokemon_id = (SELECT id FROM pokemon WHERE nome=UPPER(%s) LIMIT 1) AND rgb = %s'
            dados = (mapa_cor, pokemon_name, str(pokemon))
        else:
            query = 'INSERT INTO pokemon_color(rgb, n_ocorrencias, pokemon_id) VALUES(%s, %s, (SELECT id FROM pokemon WHERE nome=UPPER(%s) LIMIT 1))'
            dados = (str(pokemon), mapa_cor, pokemon_name)

        cursor.execute(query, dados)

    con.commit()
    cursor.close()
    con.close()

# Define qual Pokemon o dicionario representa
def get(dicionario_ocorrencia):
    # pylint: disable=W0612,W0110
    con = conecta()
    cursor = con.cursor()

    lista_rgb = []
    for cor, ocorrencia in dicionario_ocorrencia.items():
        lista_rgb.append(str(cor))

    # Busca Pokemons compatíveis com a lista de cores que foram passadas como parâmetro
    query = "SELECT p.nome, (SELECT SUM(c2.n_ocorrencias) FROM pokemon_color c2 WHERE c2.pokemon_id=p.id AND c2.rgb NOT IN (%s)), (SELECT SUM(c2.n_ocorrencias) FROM pokemon_color c2 WHERE c2.pokemon_id=p.id AND c2.rgb IN (%s)) FROM pokemon_color c INNER JOIN pokemon p ON p.id = c.pokemon_id WHERE c.rgb IN (%s) GROUP BY p.nome;"
    clausula_in = ', '.join(map(lambda x: '%s', lista_rgb))
    query = query % (clausula_in, clausula_in, clausula_in)

    params = []
    params.extend(lista_rgb)
    params.extend(lista_rgb)
    params.extend(lista_rgb)

    cursor.execute(query, tuple(params))
    result = cursor.fetchall()

    pokemons_possiveis = []
    for line in result:
        pokemons_possiveis.append(line[0])

    # Busca cores que compõem os Pokemons encontrados
    query = "SELECT c.rgb, c.n_ocorrencias, p.nome FROM pokemon_color c INNER JOIN pokemon p ON p.id = c.pokemon_id WHERE c.pokemon_id IN (SELECT id FROM pokemon WHERE nome IN (%s));"
    clausula_in = ', '.join(map(lambda x: '%s', pokemons_possiveis))
    query = query % clausula_in

    params = []
    params.extend(pokemons_possiveis)

    cursor.execute(query, tuple(params))
    resultado = cursor.fetchall()

    cursor.close()
    con.close()

    return resultado
