from decimal import Decimal, ROUND_HALF_UP


def calcular_inss_pessoa_fisica(receita):
    """
    Calcula o INSS sobre receita para pessoa física usando a tabela progressiva
    """
    # Tabela INSS 2024 (valores mensais)
    faixas_inss = [
        (Decimal('0'), Decimal('1518.00'), Decimal('0.075'), Decimal('0.075')),
        (Decimal('1518.01'), Decimal('2793.88'), Decimal('0.09'), Decimal('0.075')),
        (Decimal('2666.68'), Decimal('4000.02'), Decimal('0.12'), Decimal('0.075')),
        (Decimal('4000.03'), Decimal('7786.01'), Decimal('0.14'), Decimal('0.075')),
    ]
    
    inss_total = Decimal('0')
    receita_restante = receita
    
    for i, (base_inicial, base_final, aliquota) in enumerate(faixas_inss):
        if receita_restante <= 0:
            break

        if receita > base_inicial and receita <= base_final:
            inss_total = receita * aliquota
    
    if inss_total == Decimal('0') and receita_restante > 0:
        # Se a receita exceder a última faixa, aplicar a alíquota máxima
        inss_total = (receita * faixas_inss[-1][2])
    
    return inss_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_irrf_pessoa_fisica(base_calculo):
    """
    Calcula o IRRF sobre a base de cálculo para pessoa física
    """
    # Tabela IRRF 2024 (valores mensais)
    faixas_irrf = [
        (Decimal('0'), Decimal('2428.80'), Decimal('0'), Decimal('0')),
        (Decimal('2428.81'), Decimal('2826.65'), Decimal('0.075'), Decimal('182.16')),
        (Decimal('2826.66'), Decimal('3751.05'), Decimal('0.15'), Decimal('394.16')),
        (Decimal('3751.06'), Decimal('4664.68'), Decimal('0.225'), Decimal('675.49')),
        (Decimal('4664.69'), Decimal('999999999'), Decimal('0.275'), Decimal('908.73')),
    ]
    
    if base_calculo <= 0:
        return Decimal('0')
    
    for base_inicial, base_final, aliquota, deducao in faixas_irrf:
        if base_inicial <= base_calculo <= base_final:
            irrf = (base_calculo * aliquota) - deducao
            return max(Decimal('0'), irrf).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return Decimal('0')


def calcular_simples_nacional_anexo_iv(receita_mensal):
    """
    Calcula a alíquota efetiva do Simples Nacional Anexo IV
    """
    receita_anual = receita_mensal * 12
    
    # Tabela Simples Nacional Anexo IV 2024
    faixas_simples = [
        (Decimal('0'), Decimal('180000'), Decimal('0.045'), Decimal('0')),
        (Decimal('180000.01'), Decimal('360000'), Decimal('0.09'), Decimal('8100')),
        (Decimal('360000.01'), Decimal('720000'), Decimal('0.102'), Decimal('12420')),
        (Decimal('720000.01'), Decimal('1800000'), Decimal('0.14'), Decimal('39780')),
        (Decimal('1800000.01'), Decimal('3600000'), Decimal('0.22'), Decimal('183780')),
        (Decimal('3600000.01'), Decimal('4800000'), Decimal('0.33'), Decimal('828000')),
    ]
    
    for base_inicial, base_final, aliquota, deducao in faixas_simples:
        if base_inicial <= receita_anual <= base_final:
            aliquota_efetiva = ((receita_anual * aliquota) - deducao) / receita_anual
            return aliquota_efetiva.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    
    # Se exceder o limite, usar a última faixa
    aliquota_efetiva = ((receita_anual * Decimal('0.33')) - Decimal('828000')) / receita_anual
    return aliquota_efetiva.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

# CALCULOS

def calcular_pessoa_fisica(receita, despesas, folha_pagamento, aliquota_issqn, issqn_fixo):
    """
    Calcula todos os tributos para Pessoa Física (Livro Caixa)
    """
    resultado = {}
    
    # INSS sobre Receita
    resultado['inss_receita'] = Decimal(str(float(receita) * 0.11)) if receita < 8157.41 else Decimal(str(8157.41 * 0.11))
    
    # INSS sobre Folha de Pagamento (23%)
    resultado['inss_folha'] = (folha_pagamento * Decimal('0.23')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Base de cálculo do IRRF
    base_irrf = receita - despesas - folha_pagamento - (Decimal(str((float(folha_pagamento) * 0.08))))
    resultado['irrf'] = calcular_irrf_pessoa_fisica(base_irrf)
    
    # ISSQN
    if issqn_fixo:
        resultado['issqn'] = Decimal('0')
    else:
        resultado['issqn'] = Decimal(str(float(receita) * float(aliquota_issqn/100)))
    # Total
    resultado['total'] = resultado['inss_receita'] + resultado['inss_folha'] + resultado['irrf'] + resultado['issqn']
    resultado['percentual'] = ((resultado['total'] / receita) * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return resultado


def calcular_simples_nacional(receita, pro_labore, folha_pagamento, aliquota_issqn, issqn_fixo):
    """
    Calcula todos os tributos para Empresa no Simples Nacional Anexo IV
    """
    resultado = {}
    
    # Guia do Simples Nacional
    aliquota_efetiva = calcular_simples_nacional_anexo_iv(receita)
    resultado['guia_simples'] = (receita * aliquota_efetiva).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # INSS sobre Folha de Pagamento (26,5%)
    resultado['inss_folha'] = ((folha_pagamento + pro_labore) * Decimal('0.20')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # INSS sobre Pró-labore (20%)
    resultado['inss_pro_labore'] = (pro_labore * Decimal('0.11') if pro_labore < 8157.41 else Decimal(str(8157.41 * 0.11))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # ISSQN
    if issqn_fixo:
        resultado['issqn'] = Decimal('0')
    else:
        resultado['issqn'] = Decimal(str(float(receita) * float(aliquota_issqn)/100))

    # Total
    resultado['total'] = resultado['guia_simples'] + resultado['inss_folha'] + resultado['inss_pro_labore'] + resultado['issqn']
    resultado['percentual'] = ((resultado['total'] / receita) * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return resultado


def calcular_lucro_presumido(receita, pro_labore, folha_pagamento, aliquota_issqn, issqn_fixo):
    """
    Calcula todos os tributos para Empresa no Lucro Presumido
    """
    resultado = {}
    
    # PIS/COFINS (3,65%)
    resultado['pis_cofins'] = (receita * Decimal('0.0365')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # INSS sobre Folha de Pagamento (26,5%)
    resultado['inss_folha'] = ((folha_pagamento + pro_labore) * Decimal('0.288')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # INSS sobre Pró-labore (20%)
    resultado['inss_pro_labore'] = (pro_labore * Decimal('0.11') if pro_labore < 8157.41 else Decimal(str(8157.41 * 0.11))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # ISSQN
    if issqn_fixo:
        resultado['issqn'] = Decimal('0')
    else:
        resultado['issqn'] = Decimal(str(float(receita) * float(aliquota_issqn if aliquota_issqn < 2 else aliquota_issqn/100)))
    
    # IRPJ/CSLL
    base_presumida = receita * Decimal('0.32')
    irpj = base_presumida * Decimal('0.15')
    csll = base_presumida * Decimal('0.09')
    
    # IRPJ adicional (se receita trimestral > R$ 180.000)
    receita_trimestral = receita * 3
    if receita_trimestral > Decimal('180000'):
        excedente = receita_trimestral - Decimal('180000')
        adicional_irpj = (excedente * Decimal('0.10')) / 3
    else:
        adicional_irpj = Decimal('0')
    
    resultado['irpj_csll'] = (irpj + csll + adicional_irpj).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Total
    resultado['total'] = resultado['pis_cofins'] + resultado['inss_folha'] + resultado['inss_pro_labore'] + resultado['issqn'] + resultado['irpj_csll']
    resultado['percentual'] = ((resultado['total'] / receita) * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return resultado

