SET search_path TO projeto_f1;

CREATE TABLE IF NOT EXISTS users (
    userid SERIAL PRIMARY KEY,
    login VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Admin', 'Escuderia', 'Piloto')),
    id_original INTEGER
);

CREATE TABLE IF NOT EXISTS users_log (
    logid SERIAL PRIMARY KEY,
    userid INTEGER REFERENCES users(userid),
    acao VARCHAR(20) NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);