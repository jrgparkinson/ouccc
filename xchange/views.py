from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

#from django.contrib.auth.views import logout

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from .forms import UserRegistrationForm
from django.db.models import Q
from .models import Share, Trade, Investor, Runner, OpenTrade

from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
import json

def index(request):
	# context = {}
	# return render(request, 'xchange.html', context)

	# return dashboard(request)

	return marketplace(request)

def dashboard(request):

	if request.user.is_authenticated:
		investor = request.user.investor

		shares = Share.objects.filter(owner=request.user.investor)
		collated_shares = investor.get_shares()
		return render(request, 'dashboard.html', {'shares': shares, 'collated_shares': collated_shares})
	else:
		return render(request, 'xchange.html', {})

def profile(request):
	if request.user.is_authenticated:
		#shares = Share.objects.filter(owner=request.user.investor)
		return render(request, 'profile.html', {})
	else:
		return render(request, 'xchange.html', {})

def marketplace(request):
	if request.user.is_authenticated:
		#shares = Share.objects.filter(owner=request.user.investor)

		# Remove testing:
		#investor = request.user.investor
		#open_trade = OpenTrade.objects.filter(buyer=investor).first()
		#investor.can_fulfil_trade(open_trade)

		return render(request, 'marketplace.html', {})
	else:
		return render(request, 'xchange.html', {})

@login_required
def marketplace_buying(request):

	# Get open trades where the buyer is known
	buy_trades = OpenTrade.objects.filter(Q(status=Trade.PENDING)).order_by('-updated')

	return render(request, 'marketplace_buy.html', {'buy_trades': buy_trades})

@login_required
def marketplace_selling(request):

	# Get trades where someone wants to sell a share but there is no buyer
	sell_trades = Trade.objects.filter(Q(buyer=None) & Q(status=Trade.PENDING)).order_by('-updated')

	return render(request, 'marketplace_sell.html', {'sell_trades': sell_trades})



@login_required
def get_direct_trades(investor):
	direct_trades = Trade.objects.filter(((Q(buyer=investor) & ~Q(seller=None)) | Q(seller=investor) & ~Q(buyer=None))  & Q(status=Trade.PENDING)).order_by('-updated')

	return direct_trades

@login_required
def get_marketplace_sell_trades(investor):
	sell_trades = Trade.objects.filter(Q(seller=investor) & Q(buyer=None) & Q(status=Trade.PENDING)).order_by('-updated')

	return sell_trades

@login_required
def get_marketplace_buy_trades(investor):

	buy_trades = OpenTrade.objects.filter(Q(buyer=investor) & Q(status=Trade.PENDING)).order_by('-updated')

	return buy_trades

@login_required
def incoming_trades(request):

	investor = request.user.investor

	# Direct trades - i.e. both buyer and seller are defined, and this user is one of them
	direct_trades = get_direct_trades(investor)

	# Open trades where this is the seller
	buy_trades = get_marketplace_buy_trades(investor)

	sell_trades = get_marketplace_sell_trades(investor)

	return render(request, 'incoming_trades.html', {'direct_trades': direct_trades, 'buy_trades': buy_trades, 'sell_trades': sell_trades})

 
@login_required
def past_trades(request):

	investor = request.user.investor
	past_trades = Trade.objects.filter((Q(buyer=investor) | Q(seller=investor)) & ~Q(status=Trade.PENDING) ).order_by('-updated')

	return render(request, 'past_trades.html', {'past_trades': past_trades})

@login_required
def make_trade(request):

	investor = request.user.investor

	#shares = Share.objects.filter(owner=investor)
	sellable_shares = investor.get_sellable_shares()

	print(sellable_shares)

	# Get all shares excluding those from the current investor
	all_collated_shares = Investor.get_all_shares(investor)
	
	other_investors = Investor.objects.filter(~Q(user = request.user))

	return render(request, 'make_trade.html', {'sellable_shares': sellable_shares, 'other_investors': other_investors,
		'all_collated_shares': all_collated_shares})	
 

def get_investors_for_runner_obj(runner):
	shares = Share.objects.filter(Q(runner=runner))

	print('Shares for runner' + str(shares))

	# Now get a list of investors who own these shares, and how many they own each
	investors = []

	for s in shares:
		
		investor = s.owner

		#Check if we already have this investor
		investor_exists = False
		for i in investors:
			if i['investor_id'] == investor.id:
				investor_exists = True
				i['num_shares'] = i['num_shares'] + 1

		if not investor_exists:
			investors.append({'investor_id': investor.id, 'investor_name': str(investor), 'num_shares': 1})

	print(investors)

	return investors

def get_investors_for_runner(request):
	print('get_investors_for_runner')

	status = 0

	runner_id = int(request.GET['runner_id'])
	print('Runner id: ' + str(runner_id))
	
	runner = Runner.objects.get(pk=runner_id)

	print('Get investors for runner: ' + str(runner))
	
	investors =  get_investors_for_runner_obj(runner)

	#investors = []
	payload = {'investors': investors}

	return HttpResponse(json.dumps(payload), content_type='application/json')


@login_required
def create_trade(request):

	status = 0
	err_msg = 'Unknown error, sorry!'

	#'user_id': user_id, 'runner_id': runner_id, 'num_shares': num_shares, 'share_price': share_price, 'trade_width': trade_width}


	seller_id = int(request.GET['seller_id'])
	runner_id = int(request.GET['runner_id'])
	num_shares = float(request.GET['num_shares'])
	share_price = float(request.GET['share_price'])
	buyer_id = int(request.GET['buyer_id'])

	print('Create trade - got details')

	# Basic form checks
	if not int(num_shares) == num_shares:
		status = 4
		err_msg = 'Number of shares must be an integer'

	num_shares = int(num_shares)

	if share_price <= 0:
		status = 5
		err_msg = 'Share price must be greater than 0'

	if not status == 0:
		payload = {'status': status, 'err_msg': err_msg}
		return HttpResponse(json.dumps(payload), content_type='application/json')

	# Check trade is legit. i.e. that seller has enough shares


        #	1) You're trying to sell more shares than you have
        #	2) You're trying to buy more shares than someone has
        #	3) You're trying to spend more money than you have

	runner = Runner.objects.get(pk=runner_id)
	creator = request.user.investor

	if seller_id > 0:
		print('Create trade - checking seller')

		seller = Investor.objects.get(pk=seller_id)

		seller_shares = Share.objects.filter(owner=seller, runner=runner)
		if seller_shares.count() < num_shares:
			status = 1
			if seller == creator:
				err_msg = 'You do not have this many shares to sell'
			else:
				err_msg = 'The seller does not have this many share to sell'

	if buyer_id > 0:
		print('Create trade - checking buyer')

		buyer = Investor.objects.get(pk=buyer_id)

		# Only care about insufficient funds if this person is proposing the trade
		if num_shares*share_price > buyer.capital and buyer == creator:
			status = 2
			err_msg = 'You do not have enough capital to make this trade'

	print('Create trade - status' + str(status))

	if status == 0:
		# Execute trade

		# Direct trade
		if buyer_id >= 0 and seller_id >= 0:
			print('Make direct trade')
			buyer = Investor.objects.get(pk=buyer_id)
			seller = Investor.objects.get(pk=seller_id)

			# Find the shares to trade
			shares = Share.objects.filter(owner=seller, runner=runner)[:num_shares]

			print('Got shares')

			for s in shares:
				print(s)
				trade = Trade.objects.create(seller=seller,buyer=buyer, price=share_price, creator=creator, share=s)
				#trade.save()

		# Known seller with specific shares
		elif seller_id >= 0:
			print('Make trade with known seller but no buyer')

			seller = Investor.objects.get(pk=seller_id)

			# Find the shares to trade
			shares = Share.objects.filter(owner=seller, runner=runner)[:num_shares]

			print('Got shares')
			for s in shares:
				print(s)
				trade = Trade.objects.create(seller=seller, share=s, price=share_price, creator=creator)	
				print('Made trade')
				#trade.save()

		# Known buyer but no specific share
		elif buyer_id >= 0:
			print('Make trade with known buyer but no seller')

			buyer = Investor.objects.get(pk=buyer_id)

			for i in range(0,num_shares):
				trade = OpenTrade.objects.create(buyer=buyer, runner=runner, price=share_price, creator=creator)
				#trade.save()

		else:
			# this should never happen - no seller or buyer
			status = -1

	print('Final status: ' + str(status))
	payload = {'status': status, 'err_msg': err_msg}
	return HttpResponse(json.dumps(payload), content_type='application/json')
	

@login_required
def respond_to_trade(request):

	trade_id = int(request.GET['trade_id'])
	response = str(request.GET['response'])

	trade = Trade.objects.get(pk=trade_id)

	# Check that this response is valid (i.e. both parties have sufficient capital, or it's being rejected)
	success = (response == Trade.REJECTED or response == Trade.CANCELLED) or trade.check_if_allowed()

	if success:
		success = trade.set_status(response)
		trade.save()
	
	payload = {'trade_allowed': success}

	return HttpResponse(json.dumps(payload), content_type='application/json')
	#return HttpResponse()

@login_required
def respond_to_open_trade(request):

	trade_id = int(request.GET['trade_id'])
	response = str(request.GET['response'])
	seller_id = int(request.GET['seller_id'])

	trade = OpenTrade.objects.get(pk=trade_id)

	success = True

	# Check that this response is valid (i.e. both parties have sufficient capital, or it's being rejected)
	if response == Trade.REJECTED or response == Trade.CANCELLED:
		trade.status = response;
		trade.save()

	else:
		# Need to convert this to a direct trade, then confirm that trade
		seller = Investor.objects.get(pk=seller_id)

		success = trade.set_status(Trade.ACCEPTED, seller, s)		
	
	payload = {'trade_allowed': success}

	return HttpResponse(json.dumps(payload), content_type='application/json')

def trades(request):
	if request.user.is_authenticated:
		investor = request.user.investor
		shares = Share.objects.filter(owner=investor)

		# Remove this testing:
		#runner = Runner.objects.get(pk=2)
		#get_investors_for_runner_obj(runner)
		#trade = Trade.objects.create(seller=investor, share=shares[0], price=1.0, creator=investor)
		#incoming_trades = get_direct_trades(investor)
		#marketplace_trades = get_marketplace_buy_trades(investor)	
		#s = investor.get_sellable_shares()


		


		collated_shares = investor.get_shares()
		other_investors = Investor.objects.filter(~Q(user = request.user))
		incoming_trades = Trade.objects.filter(Q(buyer=investor) | Q(seller=investor) & Q(status=Trade.PENDING))
		past_trades = Trade.objects.filter(Q(buyer=investor) | Q(seller=investor)) #.filter(Q(income__gte=5000) | Q(income__isnull=True))

		return render(request, 'trades.html', {'collated_shares': collated_shares, 'other_investors': other_investors, 
			'shares': shares, 'past_trades': past_trades,
			#'buy_requests': buy_requests, 'sell_requests': sell_requests
			'incoming_trades': incoming_trades
			})
	else:
		return render(request, 'xchange.html')


# Create your views here.

def register(request):
	us = request.user

	# I have no idea why the extra us.id==None criteria is needed here
	if request.user.is_authenticated and not us.id == None:
		dashboard(request)
		#return render(request, 'dashboard.html')

	else:
		if request.method == 'POST':
			form = UserCreationForm(request.POST)
			if form.is_valid():
				form.save()
				username = form.cleaned_data.get('username')
				raw_password = form.cleaned_data.get('password1')
				user = authenticate(username=username, password=raw_password)
				login(request, user)

				# Set up the profile too
				user.investor.capital = 25000000 # Start with 25 million
				user.save()
            	
				return redirect('dashboard')
	            
	            
		else:
			form = UserCreationForm()

		return render(request, 'registration.html', {'form' : form})


