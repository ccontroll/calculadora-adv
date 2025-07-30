from django.core.management.base import BaseCommand
from calculadora.models import *
import logging
from datetime import datetime, timedelta

# Configura o logger para exibir mensagens no console
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Command(BaseCommand):
    help = 'Limpa os cálculos antigos da base de dados'

    def handle(self, *args, **kwargs):
        try:
            data_atual = datetime.now()
            
            # Obtém todos os cálculos
            calculos = CalculoTributario.objects.filter(data_calculo__lt=data_atual)
            logger.info(f'Número de cálculos encontrados: {calculos.count()}')

            # Exclui todos os cálculos
            calculos.delete()
            logger.info('Todos os cálculos foram excluídos com sucesso.')

        except Exception as e:
            logger.error(f'Ocorreu um erro ao limpar os cálculos: {e}')