from django import template

register = template.Library()

@register.filter(name="sub")
def sub(value, arg):
    """Subtracts the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return ""
    
@register.filter(name="currency")
def currency(value):
    """
    Converte um valor numérico para uma string formatada como moeda brasileira (R$)
    """
    a = '{:,.2f}'.format(float(value))
    b = a.replace(',','v')
    c = b.replace('.',',')
    return c.replace('v','.')
