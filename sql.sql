-- Active: 1769904960147@@127.0.0.1@5432@music_platform_dev
-- ========================================
-- SCHEMA DO BANCO DE DADOS - PLATAFORMA DE MÚSICA
-- ========================================

-- Tabela de Usuários
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    
    -- Índices para otimização
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_ativo ON usuarios(ativo);

-- Tabela de Artistas
CREATE TABLE artistas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    genero VARCHAR(50),
    bio TEXT,
    imagem_url VARCHAR(255),
    
    CONSTRAINT nome_not_empty CHECK (LENGTH(TRIM(nome)) > 0)
);

CREATE INDEX idx_artistas_nome ON artistas(nome);
CREATE INDEX idx_artistas_genero ON artistas(genero);

-- Tabela de Álbuns
CREATE TABLE albuns (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    artista_id INTEGER NOT NULL,
    ano_lancamento INTEGER,
    capa_url VARCHAR(255),
    descricao TEXT,
    
    FOREIGN KEY (artista_id) REFERENCES artistas(id) ON DELETE CASCADE,
    CONSTRAINT ano_valido CHECK (ano_lancamento IS NULL OR 
        (ano_lancamento >= 1900 AND ano_lancamento <= EXTRACT(YEAR FROM CURRENT_DATE)))
);

CREATE INDEX idx_albuns_titulo ON albuns(titulo);
CREATE INDEX idx_albuns_artista ON albuns(artista_id);
CREATE INDEX idx_albuns_ano ON albuns(ano_lancamento);

-- Tabela de Músicas
CREATE TABLE musicas (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    album_id INTEGER NOT NULL,
    duracao INTEGER, -- duração em segundos
    arquivo_url VARCHAR(255) NOT NULL,
    numero_faixa INTEGER,
    visualizacoes INTEGER DEFAULT 0,
    
    FOREIGN KEY (album_id) REFERENCES albuns(id) ON DELETE CASCADE,
    CONSTRAINT duracao_valida CHECK (duracao IS NULL OR duracao > 0),
    CONSTRAINT visualizacoes_positivas CHECK (visualizacoes >= 0)
);

CREATE INDEX idx_musicas_titulo ON musicas(titulo);
CREATE INDEX idx_musicas_album ON musicas(album_id);
CREATE INDEX idx_musicas_visualizacoes ON musicas(visualizacoes DESC);

-- Tabela de Playlists
CREATE TABLE playlists (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    publica BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT nome_playlist_not_empty CHECK (LENGTH(TRIM(nome)) >= 3)
);

CREATE INDEX idx_playlists_usuario ON playlists(usuario_id);
CREATE INDEX idx_playlists_publica ON playlists(publica);
CREATE INDEX idx_playlists_data ON playlists(data_criacao DESC);

-- Tabela Associativa: Playlist <-> Músicas (N:N)
CREATE TABLE playlist_musicas (
    id SERIAL PRIMARY KEY,
    playlist_id INTEGER NOT NULL,
    musica_id INTEGER NOT NULL,
    posicao INTEGER DEFAULT 1,
    data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (musica_id) REFERENCES musicas(id) ON DELETE CASCADE,
    
    -- Garante que uma música não seja adicionada duas vezes na mesma playlist
    UNIQUE(playlist_id, musica_id),
    
    CONSTRAINT posicao_valida CHECK (posicao > 0)
);

CREATE INDEX idx_playlist_musicas_playlist ON playlist_musicas(playlist_id);
CREATE INDEX idx_playlist_musicas_musica ON playlist_musicas(musica_id);
CREATE INDEX idx_playlist_musicas_posicao ON playlist_musicas(playlist_id, posicao);

-- Tabela Associativa: Favoritos (Usuários <-> Músicas) (N:N)
CREATE TABLE favoritos (
    usuario_id INTEGER NOT NULL,
    musica_id INTEGER NOT NULL,
    data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (usuario_id, musica_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (musica_id) REFERENCES musicas(id) ON DELETE CASCADE
);

CREATE INDEX idx_favoritos_usuario ON favoritos(usuario_id);
CREATE INDEX idx_favoritos_musica ON favoritos(musica_id);
CREATE INDEX idx_favoritos_data ON favoritos(data_adicao DESC);

-- ========================================
-- VIEWS ÚTEIS
-- ========================================

-- View: Músicas com informações completas
CREATE VIEW vw_musicas_completas AS
SELECT 
    m.id,
    m.titulo AS musica_titulo,
    m.duracao,
    m.visualizacoes,
    m.arquivo_url,
    al.id AS album_id,
    al.titulo AS album_titulo,
    al.capa_url,
    al.ano_lancamento,
    ar.id AS artista_id,
    ar.nome AS artista_nome,
    ar.genero AS artista_genero
FROM musicas m
JOIN albuns al ON m.album_id = al.id
JOIN artistas ar ON al.artista_id = ar.id;

-- View: Estatísticas de playlists
CREATE VIEW vw_playlists_stats AS
SELECT 
    p.id,
    p.nome,
    p.usuario_id,
    p.publica,
    COUNT(pm.musica_id) AS total_musicas,
    COALESCE(SUM(m.duracao), 0) AS duracao_total_segundos
FROM playlists p
LEFT JOIN playlist_musicas pm ON p.id = pm.playlist_id
LEFT JOIN musicas m ON pm.musica_id = m.id
GROUP BY p.id, p.nome, p.usuario_id, p.publica;

-- View: Top músicas por visualizações
CREATE VIEW vw_top_musicas AS
SELECT 
    m.id,
    m.titulo AS musica_titulo,
    ar.nome AS artista_nome,
    al.titulo AS album_titulo,
    m.visualizacoes
FROM musicas m
JOIN albuns al ON m.album_id = al.id
JOIN artistas ar ON al.artista_id = ar.id
ORDER BY m.visualizacoes DESC
LIMIT 100;

-- ========================================
-- FUNÇÕES E TRIGGERS
-- ========================================

-- Função para atualizar visualizações
CREATE OR REPLACE FUNCTION incrementar_visualizacao(musica_id_param INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE musicas 
    SET visualizacoes = visualizacoes + 1 
    WHERE id = musica_id_param;
END;
$$ LANGUAGE plpgsql;

-- Trigger para validar e-mail ao inserir/atualizar usuário
CREATE OR REPLACE FUNCTION validar_email_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.email := LOWER(TRIM(NEW.email));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_email
BEFORE INSERT OR UPDATE ON usuarios
FOR EACH ROW
EXECUTE FUNCTION validar_email_trigger();

-- Trigger para reordenar posições na playlist
CREATE OR REPLACE FUNCTION reordenar_playlist_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Quando uma música é removida, reordena as seguintes
    IF TG_OP = 'DELETE' THEN
        UPDATE playlist_musicas
        SET posicao = posicao - 1
        WHERE playlist_id = OLD.playlist_id 
        AND posicao > OLD.posicao;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_reordenar_playlist
AFTER DELETE ON playlist_musicas
FOR EACH ROW
EXECUTE FUNCTION reordenar_playlist_trigger();

-- ========================================
-- DADOS DE EXEMPLO (OPCIONAL)
-- ========================================

-- Inserir artistas de exemplo
INSERT INTO artistas (nome, genero, bio) VALUES
('The Beatles', 'Rock', 'Banda britânica de rock formada em Liverpool em 1960'),
('Pink Floyd', 'Rock Progressivo', 'Banda britânica de rock progressivo'),
('Queen', 'Rock', 'Banda britânica de rock formada em Londres em 1970');

-- Inserir álbuns de exemplo
INSERT INTO albuns (titulo, artista_id, ano_lancamento) VALUES
('Abbey Road', 1, 1969),
('The Dark Side of the Moon', 2, 1973),
('A Night at the Opera', 3, 1975);

-- Inserir músicas de exemplo
INSERT INTO musicas (titulo, album_id, duracao, arquivo_url, numero_faixa) VALUES
('Come Together', 1, 259, '/static/music/come-together.mp3', 1),
('Something', 1, 182, '/static/music/something.mp3', 2),
('Time', 2, 413, '/static/music/time.mp3', 1),
('Money', 2, 382, '/static/music/money.mp3', 2),
('Bohemian Rhapsody', 3, 354, '/static/music/bohemian-rhapsody.mp3', 1);

-- ========================================
-- COMENTÁRIOS DAS TABELAS
-- ========================================

COMMENT ON TABLE usuarios IS 'Armazena informações dos usuários da plataforma';
COMMENT ON TABLE artistas IS 'Armazena informações sobre os artistas musicais';
COMMENT ON TABLE albuns IS 'Armazena informações sobre os álbuns musicais';
COMMENT ON TABLE musicas IS 'Armazena informações sobre as músicas/faixas';
COMMENT ON TABLE playlists IS 'Armazena as playlists criadas pelos usuários';
COMMENT ON TABLE playlist_musicas IS 'Tabela associativa entre playlists e músicas';
COMMENT ON TABLE favoritos IS 'Tabela associativa para músicas favoritas dos usuários';

-- ========================================
-- CONSULTAS ÚTEIS
-- ========================================

-- Buscar músicas por termo
-- SELECT * FROM vw_musicas_completas 
-- WHERE musica_titulo ILIKE '%termo%' 
--    OR album_titulo ILIKE '%termo%' 
--    OR artista_nome ILIKE '%termo%';

-- Top 10 músicas mais ouvidas
-- SELECT * FROM vw_top_musicas LIMIT 10;

-- Playlists públicas com estatísticas
-- SELECT * FROM vw_playlists_stats WHERE publica = TRUE;

-- Músicas favoritas de um usuário
-- SELECT m.*, ar.nome as artista 
-- FROM favoritos f
-- JOIN musicas m ON f.musica_id = m.id
-- JOIN albuns al ON m.album_id = al.id
-- JOIN artistas ar ON al.artista_id = ar.id
-- WHERE f.usuario_id = ?;