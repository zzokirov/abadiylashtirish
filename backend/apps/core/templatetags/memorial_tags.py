"""Ommaviy xotira sahifasi uchun o'zbekcha formatlash filtrlari."""

from django import template

register = template.Library()

UZ_MONTHS = [
    'yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun',
    'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr',
]


@register.filter
def uz_date(value) -> str:
    """datetime.date -> '10-may, 1948'."""
    if not value:
        return ''
    return f"{value.day}-{UZ_MONTHS[value.month - 1]}, {value.year}"
