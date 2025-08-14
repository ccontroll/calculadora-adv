from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class CalculoTributario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    # Opções tributárias
    issqn_fixo = models.BooleanField(default=False, verbose_name="ISSQN fixo para todos os regimes")
    aliquota_issqn = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=Decimal('3'),
        validators=[MinValueValidator(Decimal('2')), MaxValueValidator(Decimal('5'))],
        verbose_name="Alíquota de ISSQN no Município"
    )
    
    # Campos comuns
    receita_mensal = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=Decimal('25000.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Receita Mensal Média"
    )
    
    # Pessoa Física
    despesas_dedutiveis = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=Decimal('10000.00'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Despesas Dedutíveis (Pessoa Física)"
    )
    folha_pagamento_pf = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=Decimal('2500.00'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Folha de Pagamento PF"
    )
    
    # Empresas
    pro_labore = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=Decimal('1518.00'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Pró-labore Registrado"
    )
    folha_pagamento_empresa = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=Decimal('2500.00'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Folha de Pagamento Empresa"
    )
    
    data_calculo = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cálculo de {self.usuario.nome} - {self.data_calculo.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Cálculo Tributário"
        verbose_name_plural = "Cálculos Tributários"
        ordering = ['-data_calculo']

