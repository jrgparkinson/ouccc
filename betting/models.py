from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

# E.g. Varsity XC Men's race 2019
class Competition(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)

    competitors = models.ManyToManyField(Competitor)

    def __repr__(self):
        return '%s %s' % (self.name, self.start_date)

    def __str__(self):
        return self.__repr__()



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

    def __str__(self):
        return self.name

# Make sure we make new punters for new users
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Punter.objects.create(user=instance)

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


