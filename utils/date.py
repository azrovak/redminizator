from datetime import date, timedelta


def all_date_between_dates(start_date:date, end_date:date):
    for n in range(1, int ((end_date - start_date).days)):
        yield start_date + timedelta(n)