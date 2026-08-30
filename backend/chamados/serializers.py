from rest_framework import serializers

from .models import Chamado, HistoricoChamado, PerfilDemo


class PerfilDemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilDemo
        fields = ['id', 'identificador', 'nome', 'tipo']


class HistoricoChamadoSerializer(serializers.ModelSerializer):
    autor = PerfilDemoSerializer(read_only=True)

    class Meta:
        model = HistoricoChamado
        fields = [
            'id',
            'tipo_evento',
            'informacao',
            'autor',
            'status_relacionado',
            'criado_em',
        ]


class ChamadoSerializer(serializers.ModelSerializer):
    solicitante = PerfilDemoSerializer(read_only=True)
    responsavel = PerfilDemoSerializer(read_only=True)
    historico = HistoricoChamadoSerializer(many=True, read_only=True)

    class Meta:
        model = Chamado
        fields = [
            'id',
            'titulo',
            'descricao',
            'local',
            'solicitante',
            'responsavel',
            'status',
            'criado_em',
            'historico',
        ]


class ChamadoCriacaoSerializer(serializers.Serializer):
    titulo = serializers.CharField(
        max_length=200,
        error_messages={
            'required': 'O título é obrigatório.',
            'blank': 'O título é obrigatório.',
            'max_length': 'O título deve ter no máximo 200 caracteres.',
        },
    )
    local = serializers.CharField(
        max_length=200,
        error_messages={
            'required': 'O local é obrigatório.',
            'blank': 'O local é obrigatório.',
            'max_length': 'O local deve ter no máximo 200 caracteres.',
        },
    )
    descricao = serializers.CharField(
        error_messages={
            'required': 'A descrição é obrigatória.',
            'blank': 'A descrição é obrigatória.',
        },
    )


class AtualizacaoSerializer(serializers.Serializer):
    informacao = serializers.CharField(
        trim_whitespace=False,
        error_messages={
            'required': 'A informação é obrigatória.',
            'blank': 'A informação é obrigatória.',
        },
    )

    def validate_informacao(self, value):
        if not value.strip():
            raise serializers.ValidationError('A informação é obrigatória.')
        return value
