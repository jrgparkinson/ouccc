from django.shortcuts import render, render_to_response
from .models import Competition, Market, Punter, Bet, BetPlacing, Competitor
from django.http import JsonResponse
# Create your views here.

from django.http import HttpResponse


def index(request):





    context = {'title': 'Bets',
               'comps': Competition.objects.all()}

    return render(request, 'bettingHome.html', context)



def market(request, id):

    market = Market.objects.get(id=id)
    competition = Competition.objects.get(market=market)

    # Check if user has placed bet in market
    bet = None
    if request.user.is_authenticated:
        punter = Punter.objects.get(user=request.user)

        try:
            # TODO: add other bet types here
            bet = BetPlacing.objects.get(punter=punter,market=market)


        except Bet.DoesNotExist:
            bet = None

    return render_to_response('market.html', { 'market': market,
                                               'competition': competition,
                                               'bet': bet})


def place_bet(request, market_id):

    # posts = Post.objects.all()
    response_data = {}

    if request.POST.get('action') == 'post':
        competitor_id = request.POST.get('competitor')
        price = request.POST.get('price')



        comp = Competitor.objects.get(id=competitor_id)

        market = Market.objects.get(id=market_id)
        print('Competitor: ' + str(comp) + ', price: ' + str(price) + ', current user: ' + str(request.user))

        current_punter = Punter.objects.get(user=request.user)

        bet = BetPlacing.objects.create(competitor = comp, price=price, market=market, punter=current_punter)

        print('Placed bet: ' + str(bet))

        # response_data['title'] = title
        # response_data['description'] = description

        # Post.objects.create(
        #     title=title,
        #     description=description,
        # )

        return JsonResponse(response_data)

    else:
        return HttpResponse('Go away')