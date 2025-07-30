from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('calculadora/', views.calculadora, name='calculadora'),
    path('nova-consulta/', views.nova_consulta, name='nova_consulta'),
    path('historico/', views.historico, name='historico'),
    path('calculo/<int:calculo_id>/', views.detalhe_calculo, name='detalhe_calculo'),
]

