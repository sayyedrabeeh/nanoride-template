from django import template

register = template.Library()

@register.filter
def format_number(value):
    """Format large numbers with K, M, B suffixes"""
    try:
        value = float(value)
        if value >= 10000000:  # 1 Crore+
            return f"{value/10000000:.1f}Cr"
        elif value >= 100000:  # 1 Lakh+
            return f"{value/100000:.1f}L"
        elif value >= 1000:  # 1 Thousand+
            return f"{value/1000:.1f}K"
        else:
            return f"{value:.0f}"
    except (ValueError, TypeError):
        return value