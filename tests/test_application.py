import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.controllers.auth_controller import AuthController
from app.extensions import db
from app.models import Album, Artist, Music, Plan, Playlist, Subscription, Tenant, User


class ApplicationApiTestCase(unittest.TestCase):
    TEST_DESCRIPTIONS = {
        'test_listar_musicas_retorna_sucesso': 'Valida listagem de musicas e total retornado',
        'test_busca_musicas_por_termo': 'Valida busca de musicas por termo no endpoint /api/musicas',
        'test_obter_musica_inexistente': 'Valida resposta para musica inexistente',
        'test_playlists_publicas_filtram_por_tenant_do_usuario_logado': 'Valida isolamento tenant em /api/playlists/publicas para usuario logado',
        'test_usuario_nao_acessa_playlist_de_outro_tenant': 'Valida bloqueio de acesso cross-tenant em /api/playlists/<id>',
        'test_playlists_publicas_anonimas_usam_tenant_default': 'Valida tenant default em /api/playlists/publicas sem autenticacao',
        'test_billing_plans_retorna_planos_ativos': 'Valida endpoint /api/billing/plans',
        'test_webhook_checkout_atualiza_assinatura': 'Valida webhook Stripe criando/atualizando assinatura',
        'test_solicitar_reset_e_redefinir_senha': 'Valida fluxo de reset de senha por token',
        'test_login_exige_email_verificado_quando_config_ativa': 'Valida bloqueio de login sem email verificado',
        'test_tela_planos_exibe_tres_planos_e_assinatura_ativa': 'Valida tela /billing/planos com Free, Pro, Business e assinatura ativa',
        'test_trocar_plano_pela_tela_billing': 'Valida troca de plano pela tela /billing/planos',
    }

    def setUp(self):
        self.app = create_app('testing')
        self.app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            DEFAULT_TENANT_SLUG='default',
            RATE_LIMIT_ENABLED=False,
            STRIPE_WEBHOOK_SECRET=None,
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
        tenant_default = Tenant(nome='Tenant Default', slug='default')
        tenant_b = Tenant(nome='Tenant B', slug='tenant-b')
        db.session.add_all([tenant_default, tenant_b])
        db.session.flush()

        self.plan_free = Plan(
            codigo='free',
            nome='Free',
            preco_mensal_centavos=0,
            moeda='brl',
            limite_playlists_privadas=1,
            limite_usuarios=1,
            ativo=True,
        )
        self.plan_pro = Plan(
            codigo='pro',
            nome='Pro',
            preco_mensal_centavos=4900,
            moeda='brl',
            stripe_price_id='price_pro_001',
            limite_playlists_privadas=20,
            limite_usuarios=5,
            ativo=True,
        )
        db.session.add_all([self.plan_free, self.plan_pro])
        db.session.flush()

        self.user_default = User(
            nome='Usuario Default',
            email='teste@local.com',
            senha='senha123',
            tenant_id=tenant_default.id,
        )
        self.user_tenant_b = User(
            nome='Usuario Tenant B',
            email='tenantb@local.com',
            senha='senha123',
            tenant_id=tenant_b.id,
        )
        artista = Artist(nome='Artista Teste', genero='Rock')
        db.session.add_all([self.user_default, self.user_tenant_b, artista])
        db.session.flush()

        assinatura = Subscription(
            tenant_id=tenant_default.id,
            plan_id=self.plan_free.id,
            status='active',
        )
        db.session.add(assinatura)
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
        db.session.flush()

        playlist_default_publica = Playlist(
            tenant_id=tenant_default.id,
            usuario_id=self.user_default.id,
            nome='Publica Default',
            publica=True,
        )
        playlist_tenant_b_publica = Playlist(
            tenant_id=tenant_b.id,
            usuario_id=self.user_tenant_b.id,
            nome='Publica Tenant B',
            publica=True,
        )
        db.session.add_all([playlist_default_publica, playlist_tenant_b_publica])
        db.session.commit()

        self.playlist_default_publica_id = playlist_default_publica.id
        self.playlist_tenant_b_publica_id = playlist_tenant_b_publica.id

    def _login(self, email, senha='senha123'):
        response = self.client.post(
            '/auth/login',
            data={'email': email, 'senha': senha},
            follow_redirects=False,
        )
        self.assertIn(response.status_code, (302, 303))

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

    def test_playlists_publicas_filtram_por_tenant_do_usuario_logado(self):
        self._describe_test()
        self._login('teste@local.com')

        response = self.client.get('/api/playlists/publicas')
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertTrue(payload['success'])
        nomes = {item['nome'] for item in payload['playlists']}

        self.assertIn('Publica Default', nomes)
        self.assertNotIn('Publica Tenant B', nomes)
        print('[APROVADO] Endpoint retornou apenas playlists publicas do tenant do usuario logado.')

    def test_usuario_nao_acessa_playlist_de_outro_tenant(self):
        self._describe_test()
        self._login('teste@local.com')

        response = self.client.get(f'/api/playlists/{self.playlist_tenant_b_publica_id}')
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertFalse(payload['success'])
        self.assertIn('nao encontrada', payload.get('message', '').lower())
        print('[APROVADO] Usuario nao acessa playlist de outro tenant.')

    def test_playlists_publicas_anonimas_usam_tenant_default(self):
        self._describe_test()
        response = self.client.get('/api/playlists/publicas')
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertTrue(payload['success'])
        nomes = {item['nome'] for item in payload['playlists']}

        self.assertIn('Publica Default', nomes)
        self.assertNotIn('Publica Tenant B', nomes)
        print('[APROVADO] Endpoint anonimo respeitou tenant default.')

    def test_billing_plans_retorna_planos_ativos(self):
        self._describe_test()
        response = self.client.get('/api/billing/plans')
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertTrue(payload['success'])
        codigos = {p['codigo'] for p in payload['plans']}
        self.assertIn('free', codigos)
        self.assertIn('pro', codigos)
        print('[APROVADO] Endpoint de billing retornou planos ativos.')

    def test_webhook_checkout_atualiza_assinatura(self):
        self._describe_test()
        payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_123',
                    'customer': 'cus_test_123',
                    'subscription': 'sub_test_123',
                    'metadata': {
                        'tenant_id': str(self.user_default.tenant_id),
                        'plan_id': str(self.plan_pro.id),
                        'plan_code': 'pro',
                    },
                }
            },
        }

        response = self.client.post(
            '/api/billing/webhook',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

        assinatura = Subscription.query.filter_by(tenant_id=self.user_default.tenant_id).first()
        self.assertIsNotNone(assinatura)
        self.assertEqual(assinatura.plan_id, self.plan_pro.id)
        self.assertEqual(assinatura.stripe_customer_id, 'cus_test_123')
        self.assertEqual(assinatura.stripe_subscription_id, 'sub_test_123')
        self.assertEqual(assinatura.status, 'active')
        print('[APROVADO] Webhook atualizou assinatura do tenant com dados Stripe.')

    def test_solicitar_reset_e_redefinir_senha(self):
        self._describe_test()
        response = self.client.post(
            '/api/auth/solicitar-reset',
            json={'email': 'teste@local.com'},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertIn('reset_token', payload)

        redefinir = self.client.post(
            '/api/auth/redefinir-senha',
            json={'token': payload['reset_token'], 'nova_senha': 'NovaSenha123'},
        )
        self.assertEqual(redefinir.status_code, 200)
        payload_redefinir = redefinir.get_json()
        self.assertTrue(payload_redefinir['success'])

        usuario = User.query.filter_by(email='teste@local.com').first()
        self.assertTrue(usuario.check_password('NovaSenha123'))
        print('[APROVADO] Fluxo de reset de senha concluido com sucesso.')

    def test_login_exige_email_verificado_quando_config_ativa(self):
        self._describe_test()
        self.app.config['REQUIRE_EMAIL_VERIFICATION'] = True
        self.user_default.email_verificado_em = None
        db.session.commit()

        with self.app.test_request_context('/auth/login', method='POST'):
            resultado = AuthController.fazer_login('teste@local.com', 'senha123')

        self.assertFalse(resultado['success'])
        self.assertIn('verifique', resultado['message'].lower())
        print('[APROVADO] Login bloqueado para conta sem email verificado.')

    def test_tela_planos_exibe_tres_planos_e_assinatura_ativa(self):
        self._describe_test()
        self._login('teste@local.com')

        response = self.client.get('/billing/planos')
        self.assertEqual(response.status_code, 200)

        html = response.get_data(as_text=True)
        self.assertIn('Free', html)
        self.assertIn('Pro', html)
        self.assertIn('Business', html)
        self.assertIn('Assinatura ativa', html)
        self.assertIn('Plano atual: <strong>Free</strong>', html)
        print('[APROVADO] Tela de planos exibiu 3 planos e assinatura ativa do tenant default.')

    def test_trocar_plano_pela_tela_billing(self):
        self._describe_test()
        self._login('teste@local.com')

        response = self.client.post(
            '/billing/planos/trocar',
            data={'plan_code': 'pro'},
            follow_redirects=False,
        )
        self.assertIn(response.status_code, (302, 303))

        assinatura = Subscription.query.filter_by(tenant_id=self.user_default.tenant_id).first()
        self.assertIsNotNone(assinatura)
        self.assertEqual(assinatura.plan_id, self.plan_pro.id)
        self.assertEqual(assinatura.status, 'active')
        print('[APROVADO] Troca de plano pela tela de billing atualizou assinatura para Pro.')


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ApplicationApiTestCase)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    if result.wasSuccessful():
        print('\nAPROVADO: todos os cenarios de teste passaram com sucesso.')
    else:
        print('\nREPROVADO: um ou mais cenarios falharam.')
