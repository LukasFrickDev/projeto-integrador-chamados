from django.urls import path

from .views import (
    ChamadoAtualizacaoView,
    ChamadoConclusaoView,
    ChamadoDetalheView,
    ChamadoInicioView,
    ChamadoListaCriacaoView,
)


urlpatterns = [
    path('chamados/', ChamadoListaCriacaoView.as_view()),
    path('chamados/<int:pk>/', ChamadoDetalheView.as_view()),
    path('chamados/<int:pk>/iniciar/', ChamadoInicioView.as_view()),
    path('chamados/<int:pk>/atualizacoes/', ChamadoAtualizacaoView.as_view()),
    path('chamados/<int:pk>/concluir/', ChamadoConclusaoView.as_view()),
]
