import datetime

from config import redmine
from utils.date import all_date_between_dates


def get_issues():
    user = redmine.user.get('current')
    return user.issues


def get_time_entries():
    user = redmine.user.get('current')
    return user.time_entries

def get_time_entry_today():
    user = redmine.user.get('current')
    _te = user.time_entries.filter(spent_on=datetime.datetime.now().date().isoformat())
    return _te

def get_empty_times():
    time_entries = get_time_entries()[:1][0]
    now_ = datetime.date.today()
    l = []
    for date in all_date_between_dates(time_entries.spent_on, now_):
        if date.isoweekday() < 6:
            l.append(str(date))
    return l