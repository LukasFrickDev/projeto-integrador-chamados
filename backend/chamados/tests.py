from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import (
    Chamado,
    HistoricoChamado,
    PerfilDemo,
    StatusChamado,
    TipoEventoHistorico,
    TipoPerfil,
)


class ModelosChamadosTests(TestCase):
    def setUp(self):
        self.solicitante = PerfilDemo.objects.create(
            identificador='solicitante-1',
            nome='Pessoa solicitante',
            tipo=TipoPerfil.SOLICITANTE,
        )
        self.manutencao = PerfilDemo.objects.create(
            identificador='manutencao-1',
            nome='Pessoa da manutenção',
            tipo=TipoPerfil.MANUTENCAO,
        )

    def test_cria_perfil_demo(self):
        self.assertEqual(self.solicitante.nome, 'Pessoa solicitante')
        self.assertEqual(self.solicitante.tipo, TipoPerfil.SOLICITANTE)
        self.assertEqual(str(self.solicitante), 'Pessoa solicitante')

    def test_novo_chamado_tem_status_aberto(self):
        chamado = Chamado.objects.create(
            titulo='Computador sem acesso à rede',
            descricao='O computador não consegue acessar a rede.',
            local='Laboratório 1',
            solicitante=self.solicitante,
        )

        self.assertEqual(chamado.status, StatusChamado.ABERTO)
        self.assertIsNotNone(chamado.criado_em)

    def test_novo_chamado_pode_ser_criado_sem_responsavel(self):
        chamado = Chamado.objects.create(
            titulo='Lâmpada queimada',
            descricao='A lâmpada do corredor está queimada.',
            local='Corredor principal',
            solicitante=self.solicitante,
        )

        self.assertIsNone(chamado.responsavel)

    def test_relacionamentos_de_solicitante_e_responsavel(self):
        chamado = Chamado.objects.create(
            titulo='Impressora parada',
            descricao='A impressora não está funcionando.',
            local='Recepção',
            solicitante=self.solicitante,
            responsavel=self.manutencao,
        )

        self.assertEqual(chamado.solicitante, self.solicitante)
        self.assertEqual(chamado.responsavel, self.manutencao)
        self.assertIn(chamado, self.solicitante.chamados_solicitados.all())
        self.assertIn(chamado, self.manutencao.chamados_responsaveis.all())

    def test_cria_e_associa_historico_ao_chamado(self):
        chamado = Chamado.objects.create(
            titulo='Porta com defeito',
            descricao='A porta não fecha corretamente.',
            local='Sala 2',
            solicitante=self.solicitante,
        )
        historico = HistoricoChamado.objects.create(
            chamado=chamado,
            tipo_evento=TipoEventoHistorico.CRIACAO,
            informacao='Chamado registrado.',
            autor=self.solicitante,
            status_relacionado=StatusChamado.ABERTO,
        )

        self.assertEqual(historico.chamado, chamado)
        self.assertEqual(list(chamado.historico.all()), [historico])

    def test_historico_tem_ordenacao_cronologica_e_desempate_estavel(self):
        chamado = Chamado.objects.create(
            titulo='Ar-condicionado sem funcionar',
            descricao='O equipamento não liga.',
            local='Sala 3',
            solicitante=self.solicitante,
        )
        primeiro = HistoricoChamado.objects.create(
            chamado=chamado,
            tipo_evento=TipoEventoHistorico.CRIACAO,
            autor=self.solicitante,
            status_relacionado=StatusChamado.ABERTO,
        )
        segundo = HistoricoChamado.objects.create(
            chamado=chamado,
            tipo_evento=TipoEventoHistorico.INICIO,
            autor=self.manutencao,
            status_relacionado=StatusChamado.EM_ANDAMENTO,
        )
        terceiro = HistoricoChamado.objects.create(
            chamado=chamado,
            tipo_evento=TipoEventoHistorico.ATUALIZACAO,
            autor=self.manutencao,
            status_relacionado=StatusChamado.EM_ANDAMENTO,
        )

        base = timezone.now()
        HistoricoChamado.objects.filter(pk=primeiro.pk).update(
            criado_em=base - timedelta(minutes=2),
        )
        HistoricoChamado.objects.filter(pk=segundo.pk).update(criado_em=base)
        HistoricoChamado.objects.filter(pk=terceiro.pk).update(criado_em=base)

        self.assertEqual(
            list(chamado.historico.all()),
            [primeiro, segundo, terceiro],
        )


class ApiChamadosTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.mariana = PerfilDemo.objects.create(
            identificador='mariana',
            nome='Mariana',
            tipo=TipoPerfil.SOLICITANTE,
        )
        self.outro_solicitante = PerfilDemo.objects.create(
            identificador='outro-solicitante',
            nome='Outro solicitante',
            tipo=TipoPerfil.SOLICITANTE,
        )
        self.rafael = PerfilDemo.objects.create(
            identificador='rafael',
            nome='Rafael',
            tipo=TipoPerfil.MANUTENCAO,
        )
        self.outra_manutencao = PerfilDemo.objects.create(
            identificador='outra-manutencao',
            nome='Outra manutenção',
            tipo=TipoPerfil.MANUTENCAO,
        )

    def cabecalho(self, perfil):
        return {'HTTP_X_DEMO_USER': perfil.identificador}

    def criar_chamado(self, solicitante=None, status=StatusChamado.ABERTO):
        return Chamado.objects.create(
            titulo='Chamado de teste',
            descricao='Descrição do chamado de teste.',
            local='Laboratório',
            solicitante=solicitante or self.mariana,
            status=status,
        )

    def iniciar_chamado(self, chamado):
        return self.client.post(
            f'/api/chamados/{chamado.pk}/iniciar/',
            **self.cabecalho(self.rafael),
        )

    def test_solicitante_cria_chamado(self):
        response = self.client.post(
            '/api/chamados/',
            {
                'titulo': 'Projetor sem imagem',
                'descricao': 'O projetor não exibe imagem.',
                'local': 'Sala 1',
                'status': StatusChamado.CONCLUIDO,
                'solicitante': self.outro_solicitante.pk,
            },
            format='json',
            **self.cabecalho(self.mariana),
        )

        chamado = Chamado.objects.get()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(chamado.solicitante, self.mariana)
        self.assertIsNone(chamado.responsavel)

    def test_chamado_criado_fica_aberto(self):
        response = self.client.post(
            '/api/chamados/',
            {
                'titulo': 'Projetor sem imagem',
                'descricao': 'O projetor não exibe imagem.',
                'local': 'Sala 1',
            },
            format='json',
            **self.cabecalho(self.mariana),
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], StatusChamado.ABERTO)

    def test_criacao_gera_historico_de_criacao(self):
        self.client.post(
            '/api/chamados/',
            {
                'titulo': 'Projetor sem imagem',
                'descricao': 'O projetor não exibe imagem.',
                'local': 'Sala 1',
            },
            format='json',
            **self.cabecalho(self.mariana),
        )

        historico = HistoricoChamado.objects.get()
        self.assertEqual(historico.tipo_evento, TipoEventoHistorico.CRIACAO)
        self.assertEqual(historico.autor, self.mariana)
        self.assertEqual(historico.status_relacionado, StatusChamado.ABERTO)

    def test_manutencao_nao_pode_criar_chamado(self):
        response = self.client.post(
            '/api/chamados/',
            {'titulo': 'Teste', 'descricao': 'Teste', 'local': 'Sala'},
            format='json',
            **self.cabecalho(self.rafael),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Chamado.objects.count(), 0)

    def test_solicitante_lista_apenas_seus_chamados(self):
        chamado_mariana = self.criar_chamado()
        self.criar_chamado(solicitante=self.outro_solicitante)

        response = self.client.get('/api/chamados/', **self.cabecalho(self.mariana))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data], [chamado_mariana.pk])

    def test_manutencao_lista_todos_os_chamados(self):
        primeiro = self.criar_chamado()
        segundo = self.criar_chamado(solicitante=self.outro_solicitante)

        response = self.client.get('/api/chamados/', **self.cabecalho(self.rafael))

        self.assertEqual(response.status_code, 200)
        self.assertEqual({item['id'] for item in response.data}, {primeiro.pk, segundo.pk})

    def test_solicitante_nao_consulta_chamado_de_outro_solicitante(self):
        chamado = self.criar_chamado(solicitante=self.outro_solicitante)

        response = self.client.get(
            f'/api/chamados/{chamado.pk}/',
            **self.cabecalho(self.mariana),
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Chamado não encontrado.')

    def test_manutencao_inicia_chamado_aberto(self):
        chamado = self.criar_chamado()

        response = self.iniciar_chamado(chamado)

        self.assertEqual(response.status_code, 200)

    def test_inicio_define_responsavel(self):
        chamado = self.criar_chamado()

        self.iniciar_chamado(chamado)
        chamado.refresh_from_db()

        self.assertEqual(chamado.responsavel, self.rafael)

    def test_inicio_altera_status_para_em_andamento(self):
        chamado = self.criar_chamado()

        self.iniciar_chamado(chamado)
        chamado.refresh_from_db()

        self.assertEqual(chamado.status, StatusChamado.EM_ANDAMENTO)

    def test_inicio_gera_historico(self):
        chamado = self.criar_chamado()

        self.iniciar_chamado(chamado)

        historico = chamado.historico.get()
        self.assertEqual(historico.tipo_evento, TipoEventoHistorico.INICIO)
        self.assertEqual(historico.autor, self.rafael)
        self.assertEqual(historico.status_relacionado, StatusChamado.EM_ANDAMENTO)

    def test_solicitante_nao_pode_iniciar_atendimento(self):
        chamado = self.criar_chamado()

        response = self.client.post(
            f'/api/chamados/{chamado.pk}/iniciar/',
            **self.cabecalho(self.mariana),
        )

        self.assertEqual(response.status_code, 403)

    def test_chamado_fora_de_aberto_nao_pode_ser_iniciado(self):
        chamado = self.criar_chamado(status=StatusChamado.EM_ANDAMENTO)

        response = self.iniciar_chamado(chamado)

        self.assertEqual(response.status_code, 400)

    def test_responsavel_registra_atualizacao_textual(self):
        chamado = self.criar_chamado()
        self.iniciar_chamado(chamado)

        response = self.client.post(
            f'/api/chamados/{chamado.pk}/atualizacoes/',
            {'informacao': 'Equipamento avaliado.'},
            format='json',
            **self.cabecalho(self.rafael),
        )

        historico = chamado.historico.latest('id')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(historico.tipo_evento, TipoEventoHistorico.ATUALIZACAO)
        self.assertEqual(historico.informacao, 'Equipamento avaliado.')

    def test_atualizacao_vazia_e_rejeitada(self):
        chamado = self.criar_chamado()
        self.iniciar_chamado(chamado)

        response = self.client.post(
            f'/api/chamados/{chamado.pk}/atualizacoes/',
            {'informacao': '   '},
            format='json',
            **self.cabecalho(self.rafael),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(chamado.historico.count(), 1)

    def test_atualizacao_antes_do_inicio_e_rejeitada(self):
        chamado = self.criar_chamado()

        response = self.client.post(
            f'/api/chamados/{chamado.pk}/atualizacoes/',
            {'informacao': 'Tentativa de atualização.'},
            format='json',
            **self.cabecalho(self.rafael),
        )

        self.assertEqual(response.status_code, 400)

    def test_atualizacao_nao_altera_status(self):
        chamado = self.criar_chamado()
        self.iniciar_chamado(chamado)

        self.client.post(
            f'/api/chamados/{chamado.pk}/atualizacoes/',
            {'informacao': 'Equipamento avaliado.'},
            format='json',
            **self.cabecalho(self.rafael),
        )
        chamado.refresh_from_db()

        self.assertEqual(chamado.status, StatusChamado.EM_ANDAMENTO)

    def test_apenas_responsavel_pode_registrar_atualizacao(self):
        chamado = self.criar_chamado()
        self.iniciar_chamado(chamado)

        response = self.client.post(
            f'/api/chamados/{chamado.pk}/atualizacoes/',
            {'informacao': 'Tentativa de outra pessoa.'},
            format='json',
            **self.cabecalho(self.outra_manutencao),
        )

        self.assertEqual(response.status_code, 403)

    def test_apenas_responsavel_pode_concluir_chamado(self):
        chamado = self.criar_chamado()
        self.iniciar_chamado(chamado)

        response = self.client.post(
            f'/api/chamados/{chamado.pk}/concluir/',
            **self.cabecalho(self.outra_manutencao),
        )
        chamado.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(chamado.status, StatusChamado.EM_ANDAMENTO)

    def test_conclusao_altera_status_para_concluido(self):
        chamado = self.criar_chamado()
        self.iniciar_chamado(chamado)

        response = self.client.post(
            f'/api/chamados/{chamado.pk}/concluir/',
            **self.cabecalho(self.rafael),
        )
        chamado.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(chamado.status, StatusChamado.CONCLUIDO)

    def test_conclusao_gera_historico(self):
        chamado = self.criar_chamado()
        self.iniciar_chamado(chamado)

        self.client.post(
            f'/api/chamados/{chamado.pk}/concluir/',
            **self.cabecalho(self.rafael),
        )

        historico = chamado.historico.latest('id')
        self.assertEqual(historico.tipo_evento, TipoEventoHistorico.CONCLUSAO)
        self.assertEqual(historico.status_relacionado, StatusChamado.CONCLUIDO)

    def test_chamado_aberto_nao_pode_ser_concluido(self):
        chamado = self.criar_chamado()

        response = self.client.post(
            f'/api/chamados/{chamado.pk}/concluir/',
            **self.cabecalho(self.rafael),
        )

        self.assertEqual(response.status_code, 400)

    def test_chamado_concluido_nao_aceita_novas_acoes(self):
        chamado = self.criar_chamado()
        self.iniciar_chamado(chamado)
        self.client.post(
            f'/api/chamados/{chamado.pk}/concluir/',
            **self.cabecalho(self.rafael),
        )

        inicio = self.iniciar_chamado(chamado)
        atualizacao = self.client.post(
            f'/api/chamados/{chamado.pk}/atualizacoes/',
            {'informacao': 'Nova tentativa.'},
            format='json',
            **self.cabecalho(self.rafael),
        )
        conclusao = self.client.post(
            f'/api/chamados/{chamado.pk}/concluir/',
            **self.cabecalho(self.rafael),
        )

        self.assertEqual(inicio.status_code, 400)
        self.assertEqual(atualizacao.status_code, 400)
        self.assertEqual(conclusao.status_code, 400)

    def test_historico_retorna_em_ordem_cronologica(self):
        resposta_criacao = self.client.post(
            '/api/chamados/',
            {
                'titulo': 'Projetor sem imagem',
                'descricao': 'O projetor não exibe imagem.',
                'local': 'Sala 1',
            },
            format='json',
            **self.cabecalho(self.mariana),
        )
        chamado_id = resposta_criacao.data['id']
        self.client.post(
            f'/api/chamados/{chamado_id}/iniciar/',
            **self.cabecalho(self.rafael),
        )
        self.client.post(
            f'/api/chamados/{chamado_id}/atualizacoes/',
            {'informacao': 'Equipamento avaliado.'},
            format='json',
            **self.cabecalho(self.rafael),
        )
        self.client.post(
            f'/api/chamados/{chamado_id}/concluir/',
            **self.cabecalho(self.rafael),
        )

        response = self.client.get(
            f'/api/chamados/{chamado_id}/',
            **self.cabecalho(self.mariana),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item['tipo_evento'] for item in response.data['historico']],
            [
                TipoEventoHistorico.CRIACAO,
                TipoEventoHistorico.INICIO,
                TipoEventoHistorico.ATUALIZACAO,
                TipoEventoHistorico.CONCLUSAO,
            ],
        )

    def test_perfil_ausente_ou_invalido_e_rejeitado(self):
        sem_perfil = self.client.get('/api/chamados/')
        perfil_invalido = self.client.get(
            '/api/chamados/',
            HTTP_X_DEMO_USER='inexistente',
        )

        self.assertEqual(sem_perfil.status_code, 403)
        self.assertEqual(perfil_invalido.status_code, 403)
