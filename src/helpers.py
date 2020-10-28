from icalendar import Calendar
from datetime import datetime,date,timedelta
import pytz
import numpy as np

def get_timerange_str(today, start_date, end_date):
    if today:
        timepoint = 'today'
    else:
        if start_date is None:
            timepoint = ''
        else:
            if end_date is None:
                timepoint = 'since {}'.format(start_date)
            else:
                timepoint = 'from {} to {}'.format(start_date,end_date)
    return timepoint

def get_today():
    time = datetime.now()
    return '{}-{}-{}'.format(time.year, time.month, time.day)

def get_tomorrow():
    time = datetime.now()+timedelta(days=1)
    return '{}-{}-{}'.format(time.year, time.month, time.day)

def get_last_week():
    time = datetime.now()-timedelta(days=7)
    return '{}-{}-{}'.format(time.year, time.month, time.day)

def get_last_month():
    time = datetime.now()-timedelta(days=31)
    return '{}-{}-{}'.format(time.year, time.month, time.day)

def read_calendar(cal_path, start_date=None, end_date=None):
    '''
    Read events in calendar from given start date
    :param cal_path:
    :param start_date: as list e.g. [2019,11,5] for 05.11.2019
    :return:
    '''
    g = open(cal_path, 'rb')
    gcal = Calendar.from_ical(g.read())

    start_date = [int(i) for i in start_date.split('-')]
    end_date = [int(i) for i in end_date.split('-')]

    # convert start and end date to datetime/date object for comparison
    if not start_date is None:
        start_date_dt = date(start_date[0], start_date[1], start_date[2])
        start_datetime_dt = datetime(start_date[0], start_date[1], start_date[2], 1, 1, 1, 1, pytz.UTC)
    if not end_date is None:
        end_date_dt = date(end_date[0], end_date[1], end_date[2])
        end_datetime_dt = datetime(end_date[0], end_date[1], end_date[2], 1, 1, 1, 1, pytz.UTC)

    reoccuring_components = []
    nonreoccuring_components = []

    # order components so that reoccuring events come after non-reoccuring ones
    for component in gcal.walk():
        if component.get('rrule') is None:
            nonreoccuring_components.append(component)
        else:
            reoccuring_components.append(component)

    seen_components = []
    components_to_keep = []

    # only keep components if they are non-duplicates in specified time window
    for component in nonreoccuring_components+reoccuring_components:
        str_version = get_str_of_component(component)
        if str_version in seen_components:
            # skip reoccuring events if an event with the same title, start and end time if already seen
            # instead keep the non-reoccuring version which contains more information, e.g. productivity score
            pass
        else:
            seen_components.append(str_version)
            if component.name == "VEVENT":
                if start_date is None:
                    if end_date is None:
                        components_to_keep.append(component)
                    elif component.get('dtstart').dt < end_datetime_dt:
                        components_to_keep.append(component)
                else:
                    try:
                        if component.get('dtstart').dt > start_datetime_dt:
                            if end_date is None:
                                components_to_keep.append(component)
                            elif component.get('dtstart').dt < end_datetime_dt:
                                components_to_keep.append(component)
                    except TypeError:
                        if component.get('dtstart').dt > start_date_dt:
                            if end_date is None:
                                components_to_keep.append(component)
                            elif component.get('dtstart').dt < end_date_dt:
                                components_to_keep.append(component)
    g.close()

    return components_to_keep

def get_str_of_component(component):
    end = component.get('dtend')
    if not end is None:
        end = end.dt
    start = component.get('dtstart')
    if not start is None:
        start = start.dt
    str_version = '{}_{}_{}'.format(component.get('summary'), start, end)
    return str_version

def filter_calendar(components, start_date, end_date):
    if not start_date is None:
        start_date_dt = date(start_date[0], start_date[1], start_date[2])
        start_datetime_dt = datetime(start_date[0], start_date[1], start_date[2], 1, 1, 1, 1, pytz.UTC)
    if not end_date is None:
        end_date_dt = date(end_date.year, end_date.month, end_date.day)
        end_datetime_dt = datetime(end_date.year, end_date.month, end_date.day, end_date.hour, end_date.minute,end_date.second, 1, pytz.UTC)
    filtered_components = []
    for component in components:
        # print(component.name)
        if component.name == "VEVENT":
            # use datetime or date based on component information
            if type(component.get('dtstart').dt)==datetime:
                start_criterion = start_datetime_dt
                end_criterion = end_datetime_dt
            else:
                start_criterion = start_date_dt
                end_criterion = end_date_dt

            if start_date is None:
                if not end_date is None:
                    filtered_components.append(component)
                elif component.get('dtstart').dt < end_criterion:
                    filtered_components.append(component)
            else:
                if component.get('dtstart').dt > start_criterion:
                    if end_date is None:
                        filtered_components.append(component)
                    elif component.get('dtstart').dt < end_criterion:
                        filtered_components.append(component)
    return filtered_components

def get_total_time(component_list):
    delta = timedelta(0)
    for component in component_list:
        # print(component.name)
        if component.name == "VEVENT":
            delta += component.get('dtend').dt-component.get('dtstart').dt
    return delta

def get_time_by_date(component_list):
    time_delta_dict = {}
    for component in component_list:
        # find start and end day
        if component.name == "VEVENT":
            try:
                component_date = component.get('dtend').dt.date()
                if component_date in time_delta_dict.keys():
                    time_delta_dict[component_date] += component.get('dtend').dt - component.get('dtstart').dt
                else:
                    time_delta_dict[component_date] = component.get('dtend').dt - component.get('dtstart').dt
            except AttributeError:
                print(component)
    return time_delta_dict

def get_prod_by_date(component_list):
    prod_dict = {}
    weighted_prod_dict = {}
    weight_dict = {} # use task time as weight
    # retrieve productivity scores per task
    for component in component_list:
        # find start and end day
        if component.name == "VEVENT":
            score = component.get('location','None')
            try:
                score = float(score)
                component_date = component.get('dtend').dt.date()
                if component_date in prod_dict.keys():
                    prod_dict[component_date].append(float(score))
                    weight_dict[component_date].append(component.get('dtend').dt - component.get('dtstart').dt)
                else:
                    prod_dict[component_date] = [float(score)]
                    weight_dict[component_date] = [component.get('dtend').dt - component.get('dtstart').dt]
            except ValueError:
                # for str that cannot be converted to float
                pass
    # weigh productivity scores by length of task, e.g. productivity of 2h task should have greater weight than 15min task
    for d in prod_dict.keys():
        times = [t.seconds/60 for t in weight_dict[d]]
        # normalise so they add up to 1
        weights = softmax(times)
        # weighted sum rather than mean
        # weighted_prod_dict[d] = sum([_x*_w for _x,_w in zip(prod_dict[d],weights)])
        weighted_prod_dict[d] = sum([_x * _w for _x, _w in zip(prod_dict[d], times)]) / sum(times)
        # prod_dict[d] = sum(prod_dict[d])/len(prod_dict[d])
    return weighted_prod_dict

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def get_avg_productivity(component_list):
    sum = 0
    scored_components = 0
    for component in component_list:
        # print(component.name)
        if component.name == "VEVENT":
            if not component.get('location') is None:
                try:
                    sum += float(component.get('location'))
                    scored_components += 1
                except ValueError:
                    pass
    if scored_components > 0:
        return sum/scored_components
    else:
        return None


def convert_dt(td):
    days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60
    return [days,hours,minutes]

