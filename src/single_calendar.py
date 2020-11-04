from helpers import read_calendar,get_total_time,convert_dt,get_today,get_last_week,get_last_month,get_tomorrow,get_avg_productivity,get_timerange_str,get_time_by_date
import argparse
import warnings

parser = argparse.ArgumentParser()
parser.register("type", "bool", lambda v: v.lower() == "true")
parser.add_argument("--today", type="bool", nargs="?", const=True, default=False, help="Only display today's data")
parser.add_argument("--this_week", type="bool", nargs="?", const=True, default=False, help="Only display this week's data")
parser.add_argument("--this_month", type="bool", nargs="?", const=True, default=False, help="Only display this month's data")
parser.add_argument('-start', action="store", dest="start", type=str, default=None, help='Start date as yyy-mm-dd')
parser.add_argument('-end', action="store", dest="end", type=str, default=None, help='End date as yyy-mm-dd')
# parser.add_argument('-project_folder', action="store", dest="project_folder", type=str, default='')


class Calendar:

    def __init__(self,file_path, start_date=None, end_date=None, today=False, this_week=False, this_month=False):
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
        self.components_total = read_calendar(file_path, self.start_date, self.end_date)
        self.name = file_path.split('/')[-1]
        self.time_delta_dict = get_time_by_date(self.components_total)
        if len(self.components_total)==0:
            no_cal_data_warning = 'No tasks found in {} calendar for period between {} and {}. Did you remember to export an up-to-date version of {} to timetrack/data/calendars/?'.format(self.name,self.start_date,self.end_date,self.name)
            warnings.warn(no_cal_data_warning)

    def print_components(self):
        components = self.components_total
        print('Tasks:')
        print('')
        for component in components:
            # print(component.name)
            if component.name == "VEVENT":
                print('{} (productivity: {})'.format(component.get('summary'),component.get('location')))  # productivity on scale of 1 (unproductive) - 5 (highly productive)
                total = component.get('dtend').dt-component.get('dtstart').dt
                print('{0:%Y-%m-%d %H:%M} - {1:%H:%M} (total: {2:})'.format(component.get('dtstart').dt,component.get('dtend').dt,total))
                # print(component.get('dtstamp').dt)
                print('')

    def get_time_summary(self, printing=True):
        timerange_str = get_timerange_str(self.today, self.start_date, self.end_date)
        components = self.components_total
        avg_productivity = get_avg_productivity(components)
        spent_time = get_total_time(components)
        if printing:
            time_list = convert_dt(spent_time)
            print('==>spent {} days {} hours {} minutes on {} tasks {}'.format(time_list[0], time_list[1], time_list[2],self.name,timerange_str))
            print('   avg productivity score: {}'.format(avg_productivity))
            print('')
        return spent_time, avg_productivity

if __name__ == '__main__':

    parser.add_argument('-calendar', action="store", dest="calendar_name", type=str, default="Meeting.ics", help='calendar name, e.g. Major.ics, Minor.ics or Meeting.ics')
    FLAGS, unparsed = parser.parse_known_args()

    cal_path = 'data/calendars/{}'.format(FLAGS.calendar_name)
    major_cal = Calendar(cal_path,FLAGS.start,FLAGS.end,FLAGS.today,FLAGS.this_week,FLAGS.this_month)
    major_cal.print_components()
    major_cal.get_time_summary()
