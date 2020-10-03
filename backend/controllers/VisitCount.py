from operators.models import TourOperator
from analytics.models import Analytic
from datetime import datetime, timedelta
from django.db.models import Count
from places.models import Country


class VisitCount():

    def __init__(self, operator: TourOperator) -> None:
        self.operator = operator
        return

    def visits_date_daily(self, date_from, date_to):
        analytics = Analytic.objects.all()
        visits = analytics.filter(activity_type=Analytic.VISIT)
        visits = visits.filter(content_type__model="touroperator")
        visits = visits.filter(object_id=self.operator.pk)
        visits = visits.filter(date_created__gte=date_from)
        visits = visits.filter(date_created__lte=date_to)
        visits = visits.extra({'date_created' : "date(date_created)"}).values('date_created').annotate(count=Count('id'))
        res = {}
        for visit in visits:
            key = visit['date_created'].strftime("%d %b")
            res[key] = "{meta:'" + key + "', value:" + str(visit['count']) + "}"
        from core.utils import daterange

        labels = []
        series = []
        count = 0
        for single_date in daterange(date_from,date_to):
            key = single_date.strftime("%d %b")
            if not key in res:
                value = "{meta:'" + key + "', value:0}"
            else:
                value = res[key]
            if count % 1 == 0:
                labels.append(key)
            else:
                labels.append('')
            series.append(value)
            count += 1
        return {
            'labels': labels,
            'series': "[" + ",".join(series) + "]",
        }

        return visits

    def _visits_date(self, date_from, date_to=False) -> int:
        analytics = Analytic.objects.all()
        visits = analytics.filter(activity_type=Analytic.VISIT)
        visits = visits.filter(content_type__model="touroperator")
        visits = visits.filter(object_id=self.operator.pk)
        visits = visits.filter(date_created__gte=date_from)
        if date_to:
            visits = visits.filter(date_created__lte=date_to)
        return visits

    def weekly(self):
        res = {}
        # last 6 days
        total_visits = 0
        for i in reversed(range(1, 7)):
            date = datetime.today() - timedelta(days=i)
            count = self._visits_date(date).count()
            res[date.strftime("%a")] = count
            total_visits += count
        # today
        date = datetime.today()
        count = self._visits_date(date).count()
        res['Today'] = count
        total_visits += count

        daynames = "','".join(res.keys())
        daynames = "['" + daynames + "']"

        return {
            'labels': daynames,
            'series': [list(res.values())],
            'total_visits': total_visits
        }

    def worldmap(self, date_from, date_to):
        res = {}
        visits = self._visits_date(date_from, date_to)
        visits_agg = visits.filter(country_short__isnull=False).exclude(country_short='').values('country_short').annotate(country_count=Count('country_short'))
        res = {x['country_short']: x['country_count'] for x in visits_agg}
        return res

    def worldtable(self, date_from, date_to):
        visits = self._visits_date(date_from, date_to)
        visits_agg = visits.filter(country_short__isnull=False).exclude(country_short='').values('country_short').annotate(country_count=Count('country_short'))
        res = {}
        total = 0
        for x in visits_agg:
            total += x['country_count']
        for x in visits_agg:
            try:
                country = Country.objects.get(iso=x['country_short'])
                percentage = x['country_count'] * 100 / total
                res[country] = (percentage, int(total * percentage/100))
            except Country.DoesNotExist:
                # return False
                pass
        return res


