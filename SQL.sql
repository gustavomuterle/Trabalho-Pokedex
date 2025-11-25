CREATE DATABASE pokedex_db;
USE pokedex_db;

CREATE TABLE treinadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(100)
);

CREATE TABLE pokemons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo1 VARCHAR(50) NOT NULL,
    tipo2 VARCHAR(50),
    treinador_id INT
);

ALTER TABLE pokemons
ADD CONSTRAINT fk_treinador
FOREIGN KEY (treinador_id)
REFERENCES treinadores(id);
