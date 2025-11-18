CREATE DATABASE pokedex_db;

CREATE TABLE treinadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(100)
);

ALTER TABLE pokemons
ADD COLUMN treinador_id INT, 
ADD FOREIGN KEY (treinador_id) REFERENCES treinadores(id);
