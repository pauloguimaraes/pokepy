CREATE DATABASE pokemon_go;

USE pokemon_go;

CREATE TABLE pokemon (
    id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(255) NOT NULL,
    PRIMARY KEY(id)
);

ALTER TABLE pokemon 
    ADD UNIQUE INDEX `ui_pokemon` (nome);

CREATE TABLE pokemon_color (
    id INT NOT NULL AUTO_INCREMENT,
    rgb VARCHAR(20) NOT NULL,
    n_ocorrencias INT NOT NULL,
    pokemon_id INT NOT NULL,
    PRIMARY KEY(id)
);

ALTER TABLE pokemon_color
    ADD CONSTRAINT `fk_pokemon` 
        FOREIGN KEY(pokemon_id) REFERENCES pokemon(id);

ALTER TABLE pokemon_color
    ADD UNIQUE INDEX `ui_pokecolor` (rgb, pokemon_id);