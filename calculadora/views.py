from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Usuario, CalculoTributario
from .forms import UsuarioForm, CalculoTributarioForm
from .utils import calcular_pessoa_fisica, calcular_simples_nacional, calcular_lucro_presumido
from decimal import Decimal
from django.core.management import call_command

def index(request):
    """
    Página inicial com formulário de cadastro do usuário
    """
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            # Extrai os dados validados do formulário
            nome = form.cleaned_data['nome']
            telefone = form.cleaned_data['telefone']
            email = form.cleaned_data['email']

            # Tenta encontrar um usuário existente pelo email E telefone
            try:
                usuario = Usuario.objects.get(email=email, telefone=telefone)
                # Se encontrou, atualiza o nome (e outros campos se houver)
                usuario.nome = nome
                usuario.save()
                messages.info(request, f'Bem-vindo de volta, {usuario.nome}! Seus dados foram atualizados.')
            except Usuario.DoesNotExist:
                # Se não encontrou, cria um novo usuário
                usuario = form.save()
                messages.success(request, f'Bem-vindo, {usuario.nome}! Agora você pode prosseguir com o planejamento tributário.')
            
            request.session['usuario_id'] = usuario.id
            call_command('limpar_calculos', verbosity=1)
            return redirect('calculadora')
    else:
        form = UsuarioForm()

    usuario_id = request.session.get('usuario_id')
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        usuario = None
    
    return render(request, 'calculadora/index.html', {'form': form, 'usuario': usuario})


def calculadora(request):
    """
    Página principal da calculadora tributária
    """
    # Verificar se o usuário está cadastrado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.warning(request, 'Por favor, faça seu cadastro primeiro.')
        return redirect('index')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado. Faça o cadastro novamente.')
        return redirect('index')
    
    if request.method == 'POST':
        form = CalculoTributarioForm(request.POST)
        if form.is_valid():
            calculo = form.save(commit=False)
            calculo.usuario = usuario
            calculo.save()
            
            # Realizar os cálculos
            resultados = realizar_calculos(calculo)
            
            return render(request, 'calculadora/calculadora.html', {
                'form': form,
                'usuario': usuario,
                'include': True,
                'calculo': calculo,
                'resultados': resultados
            })

            # return render(request, 'calculadora/resultados.html', {
            #     'calculo': calculo,
            #     'resultados': resultados,
            #     'usuario': usuario
            # })
    else:
        form = CalculoTributarioForm()
    
    return render(request, 'calculadora/calculadora.html', {
        'form': form,
        'usuario': usuario
    })


def realizar_calculos(calculo):
    """
    Realiza todos os cálculos tributários
    """
    # Parâmetros comuns
    receita = calculo.receita_mensal
    pro_labore = calculo.pro_labore
    folha_pagamento = calculo.folha_pagamento_empresa
    aliquota_issqn = calculo.aliquota_issqn
    issqn_fixo = calculo.issqn_fixo
    
    # Cálculo Pessoa Física
    pf_resultado = calcular_pessoa_fisica(
        receita=receita,
        despesas=calculo.despesas_dedutiveis,
        folha_pagamento=calculo.folha_pagamento_pf,
        aliquota_issqn=aliquota_issqn,
        issqn_fixo=issqn_fixo
    )
    
    # Cálculo Simples Nacional
    sn_resultado = calcular_simples_nacional(
        receita=receita,
        pro_labore=calculo.pro_labore,
        folha_pagamento=calculo.folha_pagamento_empresa,
        aliquota_issqn=aliquota_issqn,
        issqn_fixo=issqn_fixo
    )
    
    # Cálculo Lucro Presumido
    lp_resultado = calcular_lucro_presumido(
        receita=receita,
        pro_labore=calculo.pro_labore,
        folha_pagamento=calculo.folha_pagamento_empresa,
        aliquota_issqn=aliquota_issqn,
        issqn_fixo=issqn_fixo
    )
    
    return {
        'pessoa_fisica': pf_resultado,
        'simples_nacional': sn_resultado,
        'lucro_presumido': lp_resultado,
        'receita_mensal': receita,
        'pro_labore': pro_labore,
        'folha_pagamento': folha_pagamento
    }


def nova_consulta(request):
    """
    Limpa a sessão e redireciona para nova consulta
    """
    if 'usuario_id' in request.session:
        del request.session['usuario_id']
    messages.info(request, 'Sessão limpa. Você pode fazer uma nova consulta.')
    return redirect('index')


def historico(request):
    """
    Exibe o histórico de cálculos do usuário
    """
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.warning(request, 'Por favor, faça seu cadastro primeiro.')
        return redirect('index')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        calculos = CalculoTributario.objects.filter(usuario=usuario).order_by('-data_calculo')[:10]
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('index')
    
    return render(request, 'calculadora/historico.html', {
        'calculos': calculos,
        'usuario': usuario
    })


def detalhe_calculo(request, calculo_id):
    """
    Exibe os detalhes de um cálculo específico
    """
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.warning(request, 'Por favor, faça seu cadastro primeiro.')
        return redirect('index')
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        calculo = CalculoTributario.objects.get(id=calculo_id, usuario=usuario)
        resultados = realizar_calculos(calculo)
        
        return render(request, 'calculadora/resultados.html', {
            'calculo': calculo,
            'resultados': resultados,
            'usuario': usuario,
            'historico': True
        })
    except (Usuario.DoesNotExist, CalculoTributario.DoesNotExist):
        messages.error(request, 'Cálculo não encontrado.')
        return redirect('historico')

