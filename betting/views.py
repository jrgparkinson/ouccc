from django.shortcuts import render, render_to_response
from .models import Competition, Market, Punter, Bet, BetPlacing, Competitor, Event
from django.http import JsonResponse
# Create your views here.
from .forms import CompetitorInput
from django.contrib.admin.views.decorators import staff_member_required



from django.http import HttpResponse


def index(request):

    context = {'title': 'Bets',
               'comps': Competition.objects.all(),
               'events': Event.objects.all()}

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

    # dict of copmetitors->price
    bets = market.get_existing_bets()

    existingBets = {}
    existingBets['labels'] = ['%s (£%.2f)' % (runner, bets[runner]) for runner in list(bets.keys())] #list(bets.keys())

    existingBets['price']= [bets[k] for k in list(bets.keys())]

    print(existingBets)

    # For some reason have to had 'user' here explicitly
    return render_to_response('market.html', { 'market': market,
                                               'competition': competition,
                                               'bet': bet,
                                               'user': request.user,
                                               'existingBets': existingBets})


def place_bet(request, market_id):

    # posts = Post.objects.all()
    response_data = {}

    if request.POST.get('action') == 'post':
        competitor_id = request.POST.get('competitor')
        price = request.POST.get('price')


        comp = Competitor.objects.get(id=competitor_id)

        market = Market.objects.get(id=market_id)
        print('Competitor: ' + str(comp) + ', price: ' + str(price) + ', current user: ' + str(request.user))

        competition = market.event
        if not competition.can_place_bet:
            print('Competition has started, cannot place bet')
            response_data['error'] = 'Too late to place bet.'

        else:
            current_punter = Punter.objects.get(user=request.user)
            bet = BetPlacing.objects.create(competitor = comp, price=price, market=market, punter=current_punter)

            print('Placed bet: ' + str(bet))

        return JsonResponse(response_data)

    else:
        return HttpResponse('Go away')


