from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Chamado,
    HistoricoChamado,
    PerfilDemo,
    StatusChamado,
    TipoEventoHistorico,
    TipoPerfil,
)
from .serializers import (
    AtualizacaoSerializer,
    ChamadoCriacaoSerializer,
    ChamadoSerializer,
)

def obter_perfil_atual(request):
    identificador = request.headers.get('X-Demo-User')
    if not identificador:
        raise PermissionDenied('Perfil de demonstração inválido.')

    try:
        return PerfilDemo.objects.get(identificador=identificador)
    except PerfilDemo.DoesNotExist as error:
        raise PermissionDenied('Perfil de demonstração inválido.') from error


def obter_chamado_visivel(pk, perfil, bloquear=False):
    chamados = Chamado.objects.select_related('solicitante', 'responsavel').prefetch_related(
        'historico__autor',
    )
    if bloquear:
        chamados = chamados.select_for_update()
    if perfil.tipo == TipoPerfil.SOLICITANTE:
        chamados = chamados.filter(solicitante=perfil)
    try:
        return chamados.get(pk=pk)
    except Chamado.DoesNotExist as error:
        raise NotFound('Chamado não encontrado.') from error


def exigir_manutencao(perfil):
    if perfil.tipo != TipoPerfil.MANUTENCAO:
        raise PermissionDenied('Apenas perfis de manutenção podem executar esta ação.')


class ChamadoListaCriacaoView(APIView):
    def get(self, request):
        perfil = obter_perfil_atual(request)
        chamados = Chamado.objects.select_related('solicitante', 'responsavel').prefetch_related(
            'historico__autor',
        )
        if perfil.tipo == TipoPerfil.SOLICITANTE:
            chamados = chamados.filter(solicitante=perfil)
        return Response(ChamadoSerializer(chamados, many=True).data)

    def post(self, request):
        perfil = obter_perfil_atual(request)
        if perfil.tipo != TipoPerfil.SOLICITANTE:
            raise PermissionDenied('Apenas perfis solicitantes podem criar chamados.')

        serializer = ChamadoCriacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            chamado = Chamado.objects.create(
                solicitante=perfil,
                status=StatusChamado.ABERTO,
                **serializer.validated_data,
            )
            HistoricoChamado.objects.create(
                chamado=chamado,
                tipo_evento=TipoEventoHistorico.CRIACAO,
                autor=perfil,
                status_relacionado=StatusChamado.ABERTO,
            )
        chamado = obter_chamado_visivel(chamado.pk, perfil)
        return Response(ChamadoSerializer(chamado).data, status=status.HTTP_201_CREATED)


class ChamadoDetalheView(APIView):
    def get(self, request, pk):
        perfil = obter_perfil_atual(request)
        chamado = obter_chamado_visivel(pk, perfil)
        return Response(ChamadoSerializer(chamado).data)


class ChamadoInicioView(APIView):
    def post(self, request, pk):
        perfil = obter_perfil_atual(request)
        exigir_manutencao(perfil)
        with transaction.atomic():
            chamado = obter_chamado_visivel(pk, perfil, bloquear=True)
            if chamado.status != StatusChamado.ABERTO:
                raise ValidationError('O chamado não está aberto para início do atendimento.')
            chamado.responsavel = perfil
            chamado.status = StatusChamado.EM_ANDAMENTO
            chamado.save(update_fields=['responsavel', 'status'])
            HistoricoChamado.objects.create(
                chamado=chamado,
                tipo_evento=TipoEventoHistorico.INICIO,
                autor=perfil,
                status_relacionado=StatusChamado.EM_ANDAMENTO,
            )
        chamado = obter_chamado_visivel(chamado.pk, perfil)
        return Response(ChamadoSerializer(chamado).data)


class ChamadoAtualizacaoView(APIView):
    def post(self, request, pk):
        perfil = obter_perfil_atual(request)
        exigir_manutencao(perfil)
        serializer = AtualizacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            chamado = obter_chamado_visivel(pk, perfil, bloquear=True)
            if chamado.status != StatusChamado.EM_ANDAMENTO:
                raise ValidationError('O chamado não está em atendimento.')
            if chamado.responsavel_id != perfil.id:
                raise PermissionDenied('Apenas o responsável pode registrar atualizações.')
            HistoricoChamado.objects.create(
                chamado=chamado,
                tipo_evento=TipoEventoHistorico.ATUALIZACAO,
                informacao=serializer.validated_data['informacao'],
                autor=perfil,
                status_relacionado=StatusChamado.EM_ANDAMENTO,
            )
        chamado = obter_chamado_visivel(chamado.pk, perfil)
        return Response(ChamadoSerializer(chamado).data)


class ChamadoConclusaoView(APIView):
    def post(self, request, pk):
        perfil = obter_perfil_atual(request)
        exigir_manutencao(perfil)
        with transaction.atomic():
            chamado = obter_chamado_visivel(pk, perfil, bloquear=True)
            if chamado.status != StatusChamado.EM_ANDAMENTO:
                raise ValidationError('O chamado não está em atendimento para conclusão.')
            if chamado.responsavel_id != perfil.id:
                raise PermissionDenied('Apenas o responsável pode concluir o chamado.')
            chamado.status = StatusChamado.CONCLUIDO
            chamado.save(update_fields=['status'])
            HistoricoChamado.objects.create(
                chamado=chamado,
                tipo_evento=TipoEventoHistorico.CONCLUSAO,
                autor=perfil,
                status_relacionado=StatusChamado.CONCLUIDO,
            )
        chamado = obter_chamado_visivel(chamado.pk, perfil)
        return Response(ChamadoSerializer(chamado).data)
