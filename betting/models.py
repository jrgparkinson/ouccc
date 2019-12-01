from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from django.utils import timezone


class Club(models.Model):
    club_name = models.CharField(max_length=100)

    def __repr__(self):
        return self.club_name

    def __str__(self):
        return self.__repr__()

class Competitor(models.Model):
    name = models.CharField(max_length=100)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    def __repr__(self):
        return '%s (%s)' % (self.name, self.club)

    def __str__(self):
        return self.__repr__()

class Event(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# E.g. Varsity XC Men's race 2019
class Competition(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    # location = models.CharField(max_length=200)

    competitors = models.ManyToManyField(Competitor)

    def __repr__(self):
        return '%s %s' % (self.name, self.start_date)

    def __str__(self):
        return self.__repr__()

    @property
    def can_place_bet(self):
        return timezone.now() < self.start_date



class Team(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=100)

    def __repr__(self):
        return '%s - %s' % (self.club, self.team_name)

    def __str__(self):
        return self.__repr__()


# E.g. Women's winner
# Can be many markets per event
class Market(models.Model):

    name = models.CharField(max_length=100)
    event = models.ForeignKey(Competition, on_delete=models.CASCADE)
    # type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=PLACING)

    # Options may be a fixed list, or freeform
    # runners = models.ManyToManyField(Runner)

    def __str__(self):
        return '%s - %s' % (self.event.name, self.name)

    def get_existing_bets(self):
        '''

        :return: dict mapping competitor names to their total value
        '''


        comps_value = {}

        # Assumes bet placings"

        all_bets = BetPlacing.objects.filter(market=self)
        print(all_bets)

        for bet in all_bets:

            if bet.competitor.name in comps_value:
                comps_value[bet.competitor.name] += bet.price
            else:
                comps_value[bet.competitor.name] = bet.price

        print(comps_value)
        return comps_value


# Predict who finishes in a particular place
class MarketPlacing(Market):
    # runners = models.ManyToManyField(Competitor)
    placing = models.IntegerField()

    def __str__(self):
        return '%s - %s, Position: %s' % (self.event.name, self.name, self.placing)

# class MarketPlacing(Market):
#     # runners = models.ManyToManyField(Competitor)
#     placing = models.IntegerField()
#
#     def __str__(self):
#         return '%s - %s, Position: %s' % (self.event.name, self.name, self.placing)
#

class Punter(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    user = models.OneToOneField( get_user_model(),on_delete=models.CASCADE)

    @property
    def get_profit(self):
        #TODO
        return 0.0
    @property
    def get_ranking(self):
        profit = self.get_profit()



        if profit < 0:
            return 'Chopper'
        elif profit >=0:
            return 'Cowley Club'


    def __str__(self):
        return self.name

# Make sure we make new punters for new users
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Punter.objects.create(user=instance, name=instance.get_username())

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.punter.save()


# Links a punter, option, and market
# Can be many bets per any other object
class Bet(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    # option = models.ForeignKey(Option, on_delete=models.CASCADE)
    punter = models.ForeignKey(Punter, on_delete=models.CASCADE)
    price = models.FloatField()

    def __str__(self):
        return '%s / %s / £%s' % (self.market, self.punter, self.price)


class BetPlacing(Bet):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)

class Result(models.Model):
    runner = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    event = models.ForeignKey(Competition, on_delete=models.CASCADE)
    time = models.DurationField()
    position = models.IntegerField()

    def __str__(self):
        return '%s - %d) %s,  %s' % (self.event.name, self.runner.name, self.time, self.position)


