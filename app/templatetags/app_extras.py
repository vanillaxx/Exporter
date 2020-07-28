from app.models import Company
from django import template

register = template.Library()


@register.inclusion_tag('export/companies.html')
def get_companies():
    companies = Company.objects.all()
    return {'companies': companies}
