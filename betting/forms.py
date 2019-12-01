import csv
from django import forms
from .models import Competitor
import datetime

class CompetitorInput(forms.Form):
    file = forms.FileField()
    # place = forms.ModelChoiceField(queryset=Place.objects.all())

    def save(self):
        records = csv.reader(self.cleaned_data["file"])
        for line in records:
            input_data = Competitor()
            input_data.name = line[0]
            input_data.club = line[1]
            # input_data.time = datetime.strptime(line[1], "%m/%d/%y %H:%M:%S")
            # input_data.data_1 = line[2]
            # input_data.data_2 = line[3]
            # input_data.data_3 = line[4]
            input_data.save()


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
