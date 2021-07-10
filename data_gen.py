import datetime
import os
from os.path import join, dirname

import requests
from dotenv import load_dotenv
import pandas as pd

from utils import *
from cluster_repeat import run_algorithm

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def get_user_match(user, second_user):
    if user['id'] == second_user['id']:
        return -1
    if len(user['preference']) == 0:
        return 0
    if second_user['id'] in user['preference'][0]['colleagues']:
        return 1
    return 0


def get_user_days(user, default_days):
    if len(user['preference']) == 0:
        return default_days
    return user['preference'][0]['daysPerWeek']


def get_user_off_day(user, day_index, week_dates):
    if len(user['preference']) == 0:
        return 0
    return +(week_dates[day_index] in user['preference'][0]['awayDays'])


def get_user_event(user, day_index, week_dates, events):
    if len(events) == 0:
        return 0
    if any(event['date'] == week_dates[day_index] for event in events):
        return 1
    return 0


def get_day_objects(username):
    res = requests.get(os.environ.get('API_URL') + '/api/getPreferences?username=' + username)

    res_json = res.json()
    users = res_json['data']
    next_month_days = res_json['nextMonthDays']
    schedule_setting = res_json['scheduleSetting']
    events = res_json['events']

    default_days = schedule_setting['default_days']
    total_seats = schedule_setting['total_seats']

    month_first_day = datetime.datetime.strptime(next_month_days['startDate'], '%Y-%m-%d').date()
    month_last_day = datetime.datetime.strptime(next_month_days['endDate'], '%Y-%m-%d').date()

    week_first_day = month_first_day

    day_objects = []

    while week_first_day < month_last_day:
        print(week_first_day)

        week_dates = [(week_first_day + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]

        df = pd.DataFrame(columns=(['u' + str(users[i]['id']) for i in range(len(users))]))
        aux = pd.DataFrame(columns=(
                ['NUM_DAY'] +
                ['OFF_' + str(i + 1) for i in range(5)] +
                ['MUST_' + str(i + 1) for i in range(5)]
        ))

        for user in users:
            df.loc['u' + str(user['id'])] = [get_user_match(user, second_user) for second_user in users]
            aux.loc['u' + str(user['id'])] = (
                    [get_user_days(user, default_days)] +
                    [get_user_off_day(user, i, week_dates) for i in range(5)] +
                    [get_user_event(user, i, week_dates, events) for i in range(5)]
            )

        groups, people_groups = run_algorithm(total_seats, df, aux)

        for key in groups.keys():
            for user in groups[key]:
                day_objects.append({
                    "date": (week_first_day + datetime.timedelta(days=key-1)).strftime('%Y-%m-%d'),
                    "user_id": user
                })

        week_first_day += datetime.timedelta(days=7)

    return day_objects


if __name__ == '__main__':
    day_objects = get_day_objects('pepple')
    print(day_objects)

    # df = pd.read_excel(r'Fake Data Sherry V2.xlsx', sheet_name='Interaction V or IRL')
    # aux = pd.read_excel(r'Fake Data Sherry V2.xlsx', sheet_name='BU and Preference')
    # print(prep_aux(aux))
