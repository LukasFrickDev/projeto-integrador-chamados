from django.core.management.base import BaseCommand
from django.db import transaction

from chamados.models import (
    Chamado,
    HistoricoChamado,
    PerfilDemo,
    StatusChamado,
    TipoEventoHistorico,
    TipoPerfil,
)


class Command(BaseCommand):
    help = 'Prepara os dados demonstrativos da prova de conceito.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove os chamados existentes antes de recriar o cenário demonstrativo.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        mariana, _ = PerfilDemo.objects.update_or_create(
            identificador='mariana',
            defaults={
                'nome': 'Mariana Ribeiro',
                'tipo': TipoPerfil.SOLICITANTE,
            },
        )
        rafael, _ = PerfilDemo.objects.update_or_create(
            identificador='rafael',
            defaults={
                'nome': 'Rafael Martins',
                'tipo': TipoPerfil.MANUTENCAO,
            },
        )

        if options['reset']:
            Chamado.objects.all().delete()

        cenarios = [
            {
                'titulo': 'Lâmpada queimada na sala',
                'local': 'Sala 204',
                'descricao': 'A iluminação principal da sala não está funcionando.',
                'status': StatusChamado.ABERTO,
                'responsavel': None,
                'historico': [
                    (TipoEventoHistorico.CRIACAO, '', mariana, StatusChamado.ABERTO),
                ],
            },
            {
                'titulo': 'Ar-condicionado sem funcionar',
                'local': 'Laboratório 03',
                'descricao': 'O equipamento liga, mas não está resfriando o ambiente.',
                'status': StatusChamado.EM_ANDAMENTO,
                'responsavel': rafael,
                'historico': [
                    (TipoEventoHistorico.CRIACAO, '', mariana, StatusChamado.ABERTO),
                    (TipoEventoHistorico.INICIO, '', rafael, StatusChamado.EM_ANDAMENTO),
                    (
                        TipoEventoHistorico.ATUALIZACAO,
                        'Verificação inicial realizada. O equipamento está sendo analisado.',
                        rafael,
                        StatusChamado.EM_ANDAMENTO,
                    ),
                ],
            },
            {
                'titulo': 'Torneira com vazamento',
                'local': 'Banheiro do 2º andar',
                'descricao': 'A torneira continua pingando mesmo quando está totalmente fechada.',
                'status': StatusChamado.CONCLUIDO,
                'responsavel': rafael,
                'historico': [
                    (TipoEventoHistorico.CRIACAO, '', mariana, StatusChamado.ABERTO),
                    (TipoEventoHistorico.INICIO, '', rafael, StatusChamado.EM_ANDAMENTO),
                    (
                        TipoEventoHistorico.ATUALIZACAO,
                        'Foi identificada a necessidade de substituir o reparo da torneira.',
                        rafael,
                        StatusChamado.EM_ANDAMENTO,
                    ),
                    (TipoEventoHistorico.CONCLUSAO, '', rafael, StatusChamado.CONCLUIDO),
                ],
            },
        ]

        for cenario in cenarios:
            historico = cenario.pop('historico')
            chamado, _ = Chamado.objects.update_or_create(
                titulo=cenario['titulo'],
                local=cenario['local'],
                solicitante=mariana,
                defaults={
                    'descricao': cenario['descricao'],
                    'status': cenario['status'],
                    'responsavel': cenario['responsavel'],
                },
            )
            chamado.historico.all().delete()
            HistoricoChamado.objects.bulk_create(
                [
                    HistoricoChamado(
                        chamado=chamado,
                        tipo_evento=tipo_evento,
                        informacao=informacao,
                        autor=autor,
                        status_relacionado=status_relacionado,
                    )
                    for tipo_evento, informacao, autor, status_relacionado in historico
                ]
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Perfis preparados; 3 chamados demonstrativos; seed concluído.'
            )
        )
