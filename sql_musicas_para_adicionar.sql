-- Script para adicionar músicas de exemplo
-- Execute após criar o schema (arquivo sql.sql)

BEGIN;

-- 1) Artistas
INSERT INTO artistas (nome, genero, bio, imagem_url)
VALUES
    ('Arctic Monkeys', 'Indie Rock', 'Banda britânica formada em Sheffield.', 'https://example.com/artistas/arctic_monkeys.jpg'),
    ('Dua Lipa', 'Pop', 'Cantora e compositora britânica-albanesa.', 'https://example.com/artistas/dua_lipa.jpg'),
    ('The Weeknd', 'R&B', 'Cantor, compositor e produtor canadense.', 'https://example.com/artistas/the_weeknd.jpg');

-- 2) Álbuns
INSERT INTO albuns (titulo, artista_id, ano_lancamento, capa_url, descricao)
VALUES
    ('AM', (SELECT id FROM artistas WHERE nome = 'Arctic Monkeys' ORDER BY id DESC LIMIT 1), 2013, 'https://example.com/albuns/am.jpg', 'Quinto álbum de estúdio da banda.'),
    ('Future Nostalgia', (SELECT id FROM artistas WHERE nome = 'Dua Lipa' ORDER BY id DESC LIMIT 1), 2020, 'https://example.com/albuns/future_nostalgia.jpg', 'Álbum de pop/disco com grande sucesso mundial.'),
    ('After Hours', (SELECT id FROM artistas WHERE nome = 'The Weeknd' ORDER BY id DESC LIMIT 1), 2020, 'https://example.com/albuns/after_hours.jpg', 'Álbum com estética synthwave e hits globais.');

-- 3) Músicas
INSERT INTO musicas (titulo, album_id, duracao, arquivo_url, numero_faixa, visualizacoes)
VALUES
    ('Do I Wanna Know?',
     (SELECT id FROM albuns WHERE titulo = 'AM' ORDER BY id DESC LIMIT 1),
     272,
     'https://example.com/audio/do_i_wanna_know.mp3',
     1,
     15420),

    ('R U Mine?',
     (SELECT id FROM albuns WHERE titulo = 'AM' ORDER BY id DESC LIMIT 1),
     201,
     'https://example.com/audio/r_u_mine.mp3',
     7,
     13100),

    ('Levitating',
     (SELECT id FROM albuns WHERE titulo = 'Future Nostalgia' ORDER BY id DESC LIMIT 1),
     203,
     'https://example.com/audio/levitating.mp3',
     5,
     22780),

    ('Don''t Start Now',
     (SELECT id FROM albuns WHERE titulo = 'Future Nostalgia' ORDER BY id DESC LIMIT 1),
     183,
     'https://example.com/audio/dont_start_now.mp3',
     1,
     24250),

    ('Blinding Lights',
     (SELECT id FROM albuns WHERE titulo = 'After Hours' ORDER BY id DESC LIMIT 1),
     200,
     'https://example.com/audio/blinding_lights.mp3',
     9,
     30100),

    ('Save Your Tears',
     (SELECT id FROM albuns WHERE titulo = 'After Hours' ORDER BY id DESC LIMIT 1),
     215,
     'https://example.com/audio/save_your_tears.mp3',
     11,
     21740);

COMMIT;
