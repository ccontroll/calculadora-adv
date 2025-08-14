from django import forms
from decimal import Decimal
from .models import Usuario, CalculoTributario


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'telefone', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu nome completo',
                'required': True
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com',
                'required': True
            }),
        }


class CalculoTributarioForm(forms.ModelForm):
    class Meta:
        model = CalculoTributario
        fields = [
            'issqn_fixo', 'aliquota_issqn', 'receita_mensal',
            'despesas_dedutiveis', 'folha_pagamento_pf',
            'pro_labore', 'folha_pagamento_empresa'
        ]
        widgets = {
            'issqn_fixo': forms.Select(
                choices=[(True, 'Sim'), (False, 'Não')],
                attrs={'class': 'form-select', 'id': 'id_issqn_fixo'}
            ),
            'aliquota_issqn': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '2',
                'max': '5',
                'placeholder': '3',
                'id': 'id_aliquota_issqn'
            }),
            'receita_mensal': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '25.000,00'
            }),
            'despesas_dedutiveis': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '15.000,00'
            }),
            'folha_pagamento_pf': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '3.000,00'
            }),
            'pro_labore': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '1.518,00'
            }),
            'folha_pagamento_empresa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '3.000,00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar labels personalizados
        self.fields['issqn_fixo'].label = 'Considerar ISSQN fixo para todos os regimes?'
        self.fields['aliquota_issqn'].label = 'Alíquota de ISSQN no Município (%)'
        self.fields['receita_mensal'].label = 'Receita Mensal Média (R$)'
        self.fields['despesas_dedutiveis'].label = 'Despesas Dedutíveis (R$)'
        self.fields['folha_pagamento_pf'].label = 'Folha de Pagamento (R$)'
        self.fields['pro_labore'].label = 'Pró-labore Registrado (R$)'
        self.fields['folha_pagamento_empresa'].label = 'Folha de Pagamento (R$)'
        
        # Configurar help texts
        self.fields['issqn_fixo'].help_text = 'Selecione "Sim" se o ISSQN for cobrado de forma fixa pelo município'
        self.fields['aliquota_issqn'].help_text = 'Informe a alíquota de ISSQN aplicada no seu município (entre 2% e 5%)'
        self.fields['receita_mensal'].help_text = 'Valor médio mensal que você recebe com os serviços advocatícios'
        self.fields['despesas_dedutiveis'].help_text = 'Valor médio mensal com despesas dedutíveis (água, aluguel, energia, etc.)'
        self.fields['folha_pagamento_pf'].help_text = 'Remuneração dos funcionários registrados no CAEPF'
        self.fields['pro_labore'].help_text = 'Valor mensal do seu pró-labore como sócio da empresa'
        self.fields['folha_pagamento_empresa'].help_text = 'Total da folha de pagamento dos funcionários da empresa'

