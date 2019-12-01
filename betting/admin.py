from django.contrib import admin
from .models import *
from .forms import CsvImportForm

# Register your models here.
admin.site.register(Competition)
admin.site.register(Club)

admin.site.register(BetPlacing)
admin.site.register(MarketPlacing)

admin.site.register(Punter)
admin.site.register(Event)
admin.site.register(Result)


from django.contrib import admin
import csv
from django.urls import path
from .forms import CsvImportForm
from django.shortcuts import redirect
from django.shortcuts import render

class CompetitorAdmin(admin.ModelAdmin):

    change_list_template = "admin/betting/competitor/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            # csv_file = request.FILES["csv_file"]
            csv_file = request.FILES['csv_file'].read().decode("utf-8")

            duplicates = []
            newly_added = []

            lines = csv_file.split('\n')
            for line in lines:
                print(line)
                row = line.split(",")
                num_cols = len(row)

                if line == '':
                    continue

                if num_cols == 2:
                    name = row[0]
                    club = row[1]
                elif num_cols == 3:
                    name = '%s %s' % (row[0], row[1])
                    club = row[2]
                else:
                    print('Error row: %s' % row)
                    self.message_user(request, "Error: invalid format of csv file: %d column(s). Should be two columns, name and club, separated by a comma" % num_cols)
                    return redirect("..")

                club_obj, created = Club.objects.get_or_create(club_name=club)
                print(club_obj)
                if created:
                    club_obj.save()

                comp, created = Competitor.objects.get_or_create(name=name, club=club_obj)
                if created:
                    comp.save()
                    newly_added.append(comp)
                else:
                    duplicates.append(comp)

            response_msg = "Your csv file has been imported."

            if len(newly_added) > 0:
                response_msg = response_msg + ' %d new competitors added.' % len(newly_added)
            if len(duplicates) > 0:
                response_msg =response_msg + ' %d competitors already existed.' % len(duplicates)

            self.message_user(request, response_msg)
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/betting/csv_form.html", payload
        )

admin.site.register(Competitor, CompetitorAdmin)


