from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import locale
from django.db.models import Q
# Create your models here.

def format_currency(currency):
	locale.setlocale( locale.LC_ALL, '' )
	currency_str = locale.currency( currency, grouping=True ) + "M"
	return currency_str


# Shares organised by runner
class CollatedShare:

	def __init__(self, runner):
		self.runner = runner
		self.num_shares = 1



class CollatedShares:

	def __init__(self, shares):

		self.collated_shares = []

		for s in shares:
			self.add_share(s)

	def add_share(self, s):
		runner_exists = False
		for c in self.collated_shares:
			if c.runner == s.runner:
				c.num_shares = c.num_shares + 1
				runner_exists = True

		if not runner_exists:
			self.collated_shares.append(CollatedShare(s.runner))

	def __iter__(self):
		return iter(self.collated_shares)

	def __len__(self):
		return len(self.collated_shares)


class Investor(models.Model):
	user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
	
	capital = models.FloatField(default=25000000)

	def can_fulfil_trade(self, open_trade):
		print('Open trade: ' + str(open_trade))
		if open_trade == None:
			return False

		runner = open_trade.runner

		shares = Share.objects.filter(runner=runner, owner=self)

		print('Shares: ' + str(shares))

		if shares.count() > 0:
			return True
		else:
			return False


	def get_shares(self):
		shares = Share.objects.filter(owner=self)

		# Collate shares
		collated_shares = CollatedShares(shares)

		return collated_shares

	def get_sellable_shares(self):

		current_selling_trades = Trade.objects.filter(Q(seller=self) & Q(status=Trade.PENDING))

		current_selling_shares = []
		for t in current_selling_trades:
			current_selling_shares.append(t.share)

		all_shares = Share.objects.filter(owner=self)

		sellable_shares = []

		for s in all_shares:
			if not s in current_selling_shares:
				sellable_shares.append(s)

		collated_shares = CollatedShares(sellable_shares)

		return collated_shares

	def get_portfolio_value(self):
		# TODO: also compute value of all shares
		return self.capital

	def print_capital(self):
		#locale.setlocale()
		return format_currency(self.capital)

	def __str__(self):
		return self.user.first_name + " " + self.user.last_name


	@staticmethod
	def get_all_shares(except_investor=None):

		if except_investor == None:
			shares = Share.objects.all()

		else:

			#remove_shares = Share.objects.filter(owner=except_investor)
			shares = Share.objects.all().exclude(owner=except_investor)
			#shares = Share.objects.all().exclude(remove_shares)

		collated_shares = CollatedShares(shares)

		return collated_shares


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Investor.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.investor.save()


class Runner(models.Model):
	first_name = models.CharField(max_length=60)
	last_name = models.CharField(max_length=60)

	def __str__(self):
		return self.first_name + " " + self.last_name

class Share(models.Model):

	# Each share is owned by one person (or nobody). One person can own multiple shares.
	owner = models.ForeignKey(Investor, on_delete=models.CASCADE)

	# Each share is for one runner. One runner can be divided into multiple shares.
	runner = models.ForeignKey(Runner, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.id) + " - " + str(self.runner) + " (" + str(self.owner) + ")"

	def is_being_traded(self):
		trades = Trade.objects.filter(share=self, status=Trade.PENDING)

		if trades.count() > 0:
			return True
		else:
			return False

class AbstractTrade(models.Model):

	PENDING = 'P'
	ACCEPTED = 'A'
	REJECTED = 'R'
	CANCELLED = 'C'
	STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (CANCELLED, 'Cancelled'),
    )

	seller = models.ForeignKey(Investor, related_name="%(app_label)s_%(class)s_seller", on_delete=models.CASCADE, blank=True, null=True)
	buyer = models.ForeignKey(Investor, related_name="%(app_label)s_%(class)s_buyer", on_delete=models.CASCADE, blank=True, null=True)

	price = models.FloatField()

	creator = models.ForeignKey(Investor, related_name="%(app_label)s_%(class)s_creator", on_delete=models.CASCADE)

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	decision_dt = models.DateTimeField(blank=True, null=True)
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)


	class Meta:
		abstract = True

	def print_price(self):
		return format_currency(self.price)

	def print_status(self):
		for c in self.STATUS_CHOICES:
			if c[0] == self.status:
				return c[1]

	def __str__(self):
		return "From " + str(self.seller) + " to " + str(self.buyer)


	def check_if_allowed(self):
		if self.buyer.capital < self.price:
			return False

		return True

	def set_status(self, new_status):

		success = False

		if new_status == self.REJECTED or new_status == self.CANCELLED:
			self.status = new_status
			self.save()
			success = True

		# The 'Accepted' case needs to be handled by the derived classes

		return success





# An open trade is for some runner
class OpenTrade(AbstractTrade):
	runner = models.ForeignKey(Runner, on_delete=models.CASCADE)

	# Open trade must have a buyer, however we can't enforce that here
	#buyer = models.ForeignKey(Investor, related_name='open_trade_buyer', on_delete=models.CASCADE)

	# An open trade can be made into a specific trade
	# By a buyer or seller who has the share accepting it


	def __str__(self):
		return str(self.runner) + " from " + str(self.seller) + " to " + str(self.buyer)

	def set_status(new_status, seller, s):

		if new_status == self.REJECTED or new_status == self.CANCELLED:
			self.status = new_status
			self.save()

			success = True

		elif new_status == self.ACCEPTED:

			# Get a share in this runner belonging to the seller
			s = Share.objects.filter(owner=seller, runner=self.runner).first()
			if s == None:
				success = False

			else:

				direct_trade = Trade.objects.create(seller=seller,buyer=self.buyer, price=self.share_price, creator=self.creator, share=s)
				direct_trade.set_status(Trade.ACCEPTED)
			
				self.save()

		else:
			success = False

		return success


# A specific trade is for a particular share
class Trade(AbstractTrade):

	share = models.ForeignKey(Share, on_delete=models.CASCADE)

	# Specific trade must have a seller, however django won't let us enforce that like this
	#seller = models.ForeignKey(Investor, related_name='trade_seller', on_delete=models.CASCADE)

	def __str__(self):
		return str(self.share) + " from " + str(self.seller) + " to " + str(self.buyer)


	def set_status(self, new_status):

		success = False

		if new_status == self.REJECTED or new_status == self.CANCELLED:
			self.status = new_status
			self.save()
			success = True

		elif new_status == self.ACCEPTED:
			if self.check_if_allowed():
				self.status = new_status
				self.buyer.capital = self.buyer.capital - self.price
				self.seller.capital = self.seller.capital + self.price

				self.share.owner = self.buyer

				self.save()
				self.buyer.save()
				self.seller.save()
				self.share.save()

				success = True



		return success

			



class Dividend(models.Model):
	date_issued = models.DateTimeField()
	value = models.FloatField()

	# Each dividend is assigned to 1 runner
	runner = models.ForeignKey(Runner, on_delete=models.CASCADE)

	def __str__(self):
		locale.setlocale( locale.LC_ALL, '' )
		
		return str(self.runner) + ": " + locale.currency(self.value, grouping=True )




