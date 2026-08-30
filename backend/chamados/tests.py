from django.test import TestCase

# Create your tests here.
from datetime import timedelta

from django.utils import timezone

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
