import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db
from app.models import Album, Artist, Music, User


class ApplicationApiTestCase(unittest.TestCase):
    TEST_DESCRIPTIONS = {
        'test_listar_musicas_retorna_sucesso': 'Valida listagem de musicas e total retornado',
        'test_busca_musicas_por_termo': 'Valida busca de musicas por termo no endpoint /api/musicas',
        'test_obter_musica_inexistente': 'Valida resposta para musica inexistente',
    }

    def setUp(self):
        self.app = create_app('testing')
        self.app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            TESTING=True,
            WTF_CSRF_ENABLED=False,
        )

        self.ctx = self.app.app_context()
        self.ctx.push()

        db.create_all()
        self._seed_data()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _describe_test(self):
        description = self.TEST_DESCRIPTIONS.get(self._testMethodName, self._testMethodName)
        print(f"\n[TESTE] {description}")

    def _seed_data(self):
        usuario = User(nome='Teste', email='teste@local.com', senha='senha123')
        artista = Artist(nome='Artista Teste', genero='Rock')
        db.session.add_all([usuario, artista])
        db.session.flush()

        album = Album(titulo='Album Teste', artista_id=artista.id, ano_lancamento=2024)
        db.session.add(album)
        db.session.flush()

        musica_1 = Music(
            titulo='Primeira Musica',
            album_id=album.id,
            arquivo_url='/static/music/primeira.mp3',
            duracao=200,
            numero_faixa=1,
        )
        musica_2 = Music(
            titulo='Segunda Faixa',
            album_id=album.id,
            arquivo_url='/static/music/segunda.mp3',
            duracao=240,
            numero_faixa=2,
        )

        db.session.add_all([musica_1, musica_2])
        db.session.commit()

    def test_listar_musicas_retorna_sucesso(self):
        self._describe_test()
        response = self.client.get('/api/musicas')

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['total'], 2)
        self.assertEqual(len(payload['musicas']), 2)
        print('[APROVADO] Listagem retornou sucesso e 2 musicas.')

    def test_busca_musicas_por_termo(self):
        self._describe_test()
        response = self.client.get('/api/musicas?q=Primeira')

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['total'], 1)
        self.assertEqual(payload['musicas'][0]['titulo'], 'Primeira Musica')
        print('[APROVADO] Busca por termo encontrou apenas a faixa esperada.')

    def test_obter_musica_inexistente(self):
        self._describe_test()
        response = self.client.get('/api/musicas/999')

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertFalse(payload['success'])
        self.assertIn('encontrada', payload.get('message', '').lower())
        print('[APROVADO] Endpoint respondeu corretamente para musica inexistente.')


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ApplicationApiTestCase)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    if result.wasSuccessful():
        print('\nAPROVADO: todos os cenarios de teste passaram com sucesso.')
    else:
        print('\nREPROVADO: um ou mais cenarios falharam.')

