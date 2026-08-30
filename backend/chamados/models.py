from django.db import models


class TipoPerfil(models.TextChoices):
    SOLICITANTE = 'SOLICITANTE', 'Solicitante'
    MANUTENCAO = 'MANUTENCAO', 'Manutenção'


class StatusChamado(models.TextChoices):
    ABERTO = 'ABERTO', 'Aberto'
    EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em andamento'
    CONCLUIDO = 'CONCLUIDO', 'Concluído'


class TipoEventoHistorico(models.TextChoices):
    CRIACAO = 'CRIACAO', 'Criação'
    INICIO = 'INICIO', 'Início'
    ATUALIZACAO = 'ATUALIZACAO', 'Atualização'
    CONCLUSAO = 'CONCLUSAO', 'Conclusão'


class PerfilDemo(models.Model):
    identificador = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=150)
    tipo = models.CharField(max_length=12, choices=TipoPerfil.choices)

    def __str__(self):
        return self.nome


class Chamado(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    local = models.CharField(max_length=200)
    solicitante = models.ForeignKey(
        PerfilDemo,
        on_delete=models.PROTECT,
        related_name='chamados_solicitados',
    )
    responsavel = models.ForeignKey(
        PerfilDemo,
        on_delete=models.SET_NULL,
        related_name='chamados_responsaveis',
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=12,
        choices=StatusChamado.choices,
        default=StatusChamado.ABERTO,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} ({self.get_status_display()})'


class HistoricoChamado(models.Model):
    chamado = models.ForeignKey(
        Chamado,
        on_delete=models.CASCADE,
        related_name='historico',
    )
    tipo_evento = models.CharField(max_length=12, choices=TipoEventoHistorico.choices)
    informacao = models.TextField(blank=True)
    autor = models.ForeignKey(
        PerfilDemo,
        on_delete=models.PROTECT,
        related_name='historicos_autoria',
    )
    status_relacionado = models.CharField(max_length=12, choices=StatusChamado.choices)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em', 'id']

    def __str__(self):
        return f'{self.get_tipo_evento_display()} - {self.chamado}'

# Create your models here.
