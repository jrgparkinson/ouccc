from django import template
#from xchange.models import Share, Trade, Investor, Runner, OpenTrade

register = template.Library()

@register.simple_tag(takes_context=True)
def check_investor_can_fulfil_trade(context, open_trade):
    try:
        request = context['request']
        investor = request.user.investor
        flag = investor.can_fulfil_trade(open_trade)
        return flag
    except Exception as e:
        return ""