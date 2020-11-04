from single_calendar import *
from datetime import timedelta
from plotting import plot_multi_cal_time
from helpers import get_prod_by_date

class MultiCalendar:

    def __init__(self, start_date=None, end_date=None, calendars=['Major.ics','Minor.ics','Meeting.ics'],today=False,this_week=False,this_month=False,print_details=False):
        self.today = today
        if today:
            self.start_date = get_today()
            self.end_date = get_tomorrow()
        elif this_week:
            self.start_date = get_last_week()
            self.end_date = get_tomorrow()
        elif this_month:
            self.start_date = get_last_month()
            self.end_date = get_tomorrow()
        else:
            self.start_date = start_date
            self.end_date = end_date
        self.calendars = [Calendar('data/calendars/{}'.format(cal), self.start_date, self.end_date) for cal in calendars]
        nonempty_calendars = [len(c.components_total)>0 for c in self.calendars]
        if not True in nonempty_calendars:
            no_cal_data_error = 'No calendar data found between {} and {}. Please make sure to export an up-to-date version of your calendars to your timetrack/data/calendars/ folder.'.format(
                self.start_date, self.end_date)
            raise ValueError(no_cal_data_error)
        self.productivity_dict = self.get_productivity_dict()
        self.print_details = print_details

    def get_productivity_dict(self):
        # aggregate component productivity scores from all calendars by date
        all_comps = []
        for cal in self.calendars:
            all_comps += cal.components_total
        return get_prod_by_date(all_comps)

    def get_time_summary(self, printing=True):
        # get data
        timepoint_str = get_timerange_str(FLAGS.today, self.start_date, self.end_date)
        times = []
        prod_scores = []
        names = []
        total_time = timedelta(0)
        for cal in self.calendars:
            time_spent, productivity = cal.get_time_summary(False)
            times.append(time_spent)
            prod_scores.append(productivity)
            names.append(cal.name)
            total_time += time_spent

        if printing:
            time_list = convert_dt(total_time)
            print('==>spent {} days {} hours {} minutes on tasks {}'.format(time_list[0], time_list[1], time_list[2],timepoint_str))
            for cal_name,timing,prod in zip(names,times,prod_scores):
                time_list = convert_dt(timing)
                if prod is None:
                    prod_str = 'N/A'
                else:
                    prod_str = round(prod, 1)
                print('   - {} tasks: {} days {} hours {} minutes (avg. productivity: {})'.format(cal_name,time_list[0], time_list[1], time_list[2],prod_str))
            print('')
        return times, names, prod_scores

    def plot_time_summary(self,prod_score,all_days):
        names = [cal.name for cal in self.calendars]
        time_delta_dicts = [cal.time_delta_dict for cal in self.calendars]
        plot_multi_cal_time(names,time_delta_dicts,self.productivity_dict,plot_productivity=prod_score,plot_all_days=all_days,print_details=self.print_details)


if __name__ == '__main__':


    parser.add_argument("-calendars", type=str, nargs="?", const=True, default="Major.ics,Minor.ics,Meeting.ics", help="Names of calendars to load separated by comma, e.g.: Major.ics,Minor.ics,Meeting.ics")
    parser.add_argument("--prod_score", type="bool", nargs="?", const=True, default=False, help="Plot productivity scores.")
    parser.add_argument("--all_days", type="bool", nargs="?", const=True, default=False, help="Plot all days, even those without tasks.")
    parser.add_argument("--print_details", type="bool", nargs="?", const=True, default=False, help="Print time spent per calendar category per day.")

    FLAGS = parser.parse_args()

    calendars = FLAGS.calendars.split(',')

    multi_cal = MultiCalendar(FLAGS.start,FLAGS.end,calendars,FLAGS.today,FLAGS.this_week,FLAGS.this_month,FLAGS.print_details) # for one day: set start date, end date + 1
    times, names, prod_scores = multi_cal.get_time_summary()
    multi_cal.plot_time_summary(FLAGS.prod_score,FLAGS.all_days)
    # major_cal.print_components(today=True)
    # major_cal.get_spent_time(today=True)
