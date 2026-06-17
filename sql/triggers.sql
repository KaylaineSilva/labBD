
SET search_path TO projeto_f1;
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- Necessário para gerar senhas seguras usando a função gen_random_uuid()

-- Trigger para criar usuário do tipo "Escuderia" automaticamente ao cadastrar uma nova escuderia
CREATE OR REPLACE FUNCTION criar_usuario_escuderia()
RETURNS TRIGGER AS $$
BEGIN
    -- Verifica se o usuário já existe para a escuderia
    IF EXISTS (
        SELECT 1 FROM users WHERE login = NEW.constructor_ref || '_c'
        ) THEN
            RAISE EXCEPTION 'Usuário para a escuderia % já existe. Nenhum novo usuário será criado.', NEW.constructor_ref; 
            -- cancelando a operação de inserção do usuário, pois já existe um para essa escuderia
    ELSE
        -- Insere um novo usuário do tipo "Escuderia" com login baseado no nome da escuderia
        INSERT INTO users (login, password, tipo, id_original)
        VALUES (
            NEW.constructor_ref || '_c',
            crypt(NEW.constructor_ref, gen_salt('bf')), 
            'Escuderia', 
            NEW.id
            );
        RETURN NEW;

    END IF;

END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_criar_usuario_escuderia ON constructors;

-- Caso haja uma inserção de escuderia, o trigger irá fazer a verificação se a escuderia já não existe e criar um usuário do tipo "Escuderia" automaticamente, caso exista, o trigger irá apenas emitir um aviso e não criar um novo usuário, evitando duplicidade. 
CREATE TRIGGER trigger_criar_usuario_escuderia
AFTER INSERT ON constructors
FOR EACH ROW
EXECUTE FUNCTION criar_usuario_escuderia();