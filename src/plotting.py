# libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib import pyplot
from datetime import timedelta

def autolabel(ax, bar_plot, existing_bar_heights, bar_label, fontweight='bold', color='black', position='middle'):
    for idx, (rect, existing_bar_height) in enumerate(zip(bar_plot, existing_bar_heights)):
        if position == 'bottom':
            height = 0
            offset = 1.01
        elif position == 'middle':
            height = rect.get_height() / 2 + existing_bar_height
            offset = 0.97
        elif position == 'top':
            height = rect.get_height() + existing_bar_height
            offset = 1.01
        ax.text(rect.get_x() + rect.get_width() / 2., offset * height,
                bar_label[idx],
                ha='center', va='bottom', rotation=0, fontweight=fontweight, color=color)

def get_max_bar_height(bar_plot, existing_bar_heights):
    heights = []
    for idx, (rect, existing_bar_height) in enumerate(zip(bar_plot, existing_bar_heights)):
        heights.append(rect.get_height() + existing_bar_height)
    return max(heights)

def plot_multi_cal_time(names, time_delta_dicts, productivity_dict, granularity = 'hours', label_time=True, label_day=True, plot_productivity=True, plot_all_days=True,print_details=True):
    # y-axis in bold
    rc('font', weight='bold')

    # prepare data to plot

    assert len(names)==len(time_delta_dicts)
    assert granularity in ['minutes','hours','days']
    weekdays = ['M','Tu','W','Th','Fr','Sa','Su']

    # get unique sorted dates

    all_keys = []
    for delta_dict in time_delta_dicts:
        all_keys += list(delta_dict.keys())
    if plot_all_days: # fill in dates without tasks
        all_unique_keys = []
        start = min(all_keys)
        end = max(all_keys)
        current = start
        while True:
            all_unique_keys.append(current)
            if current==end:
                break
            else:
                current+=timedelta(days=1)
    else:
        all_unique_keys = list(set(all_keys))
        all_unique_keys.sort()

    calendars = [[] for c in range(len(time_delta_dicts))]
    timepoints = []
    days = []

    for date in all_unique_keys:
        if date not in productivity_dict.keys():
            productivity_dict[date]=None

        timepoints.append('{0:%d/%m}'.format(date,weekdays[date.isoweekday()-1]))
        days.append('{}'.format(weekdays[date.isoweekday()-1]))

        if print_details:
            print('{} ({})'.format(date, weekdays[date.isoweekday() - 1]))

        for i,(cal_name,delta_dict) in enumerate(zip(names,time_delta_dicts)):

            # fill in any missing values
            if not date in delta_dict.keys():
                delta_dict[date] = timedelta(0)

            # print info for verification
            if print_details:
                print('{}: {}'.format(cal_name,delta_dict[date]))

            # get times at in requested unit
            if granularity=='days':
                calendars[i].append(delta_dict[date].days)
            elif granularity=='hours':
                calendars[i].append(delta_dict[date].total_seconds()/60/60)
            elif granularity=='minutes':
                calendars[i].append(delta_dict[date].total_seconds()/60)

    assert len(calendars)==len(time_delta_dicts)

    # The position of the bars on the x-axis
    r = [i for i in range(len(all_unique_keys))]

    # todo: add values to stacked bars, e.g. https://stackoverflow.com/questions/44309507/stacked-bar-plot-using-matplotlib

    # Names of group and bar width = dates
    # timepoints = ['today']#['A', 'B', 'C', 'D', 'E']
    barWidth = 1

    axes1 = plt.subplot(111)

    # found with Digital Color Meter on Mac
    # colours = ['#7f6d5f','#557f2d','#2d7f5e','#2d7f5e']
    colours_pref_dark = {'Major.ics':'#246BC3',  #'#2B89FB', # blue
                    'Minor.ics':'#BD8D25',  #FCCF42', # yellow/orange
                    'Meeting.ics':'#7F4083',  #CE83E1', # pink
                    'Life.ics':'#0F881D',  #75DA56', # green
                    'Health.ics': '#0F881D',  # 75DA56', # green
                    'Travel.ics':'#545454'} #878787'} # grey
    colours_pref_light = {'Major.ics':'#CEDFFD', # blue
                    'Minor.ics':'#FFF4CD', # yellow/orange
                    'Meeting.ics':'#F4E3F8', # pink
                    'Life.ics':'#E0F6D8', # green
                    'Health.ics':'#E0F6D8', # green
                    'Travel.ics':'#E0E0E0'} # grey

    for i in range(len(calendars)):
        # initial start height of bars = 0
        bars = [0 for i in range(len(all_unique_keys))]
        # add up values from previous bars for correct start height of next bar
        for p in range(i):
            bars = np.add(bars,calendars[p])
        # convert back to list if necessary
        if not type(bars) == list:
            bars = bars.tolist()
        if names[i] in colours_pref_light.keys():
            bar_plot = plt.bar(r, calendars[i], bottom=bars, color=colours_pref_light[names[i]], edgecolor=colours_pref_dark[names[i]], width=barWidth, label=names[i])
        else:
            bar_plot = plt.bar(r, calendars[i], bottom=bars, edgecolor='white', width=barWidth, label=names[i])
        # annotate time values
        if label_time:
            values = []
            for time in calendars[i]:
                time = round(time, 1)
                # don't annotate tiny time chunks to avoid clutter
                if time > 0.5:
                    values.append(time)
                else:
                    values.append('')
            autolabel(axes1, bar_plot, bars, values,color=colours_pref_dark[names[i]])

    # if label bars
    if label_day:
        autolabel(axes1, bar_plot,bars,days, position='top')

    # Custom X axis
    if len(timepoints)>10:
        plt.xticks(r, timepoints, fontweight='bold',rotation=90)
    else:
        plt.xticks(r, timepoints, fontweight='bold')

    plt.xlabel('Day')
    plt.ylabel("Time in {}".format(granularity))
    max_y = get_max_bar_height(bar_plot, bars)+0.5
    axes1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1),
              fancybox=True, shadow=True, ncol=len(names))
    axes1.set_ylim(0,max_y)

    for threshold in [8]: # dashed line in plot
        axes1.plot([-0.5, len(all_unique_keys)-0.5], [threshold, threshold],"k--",linewidth=1,color='grey')


    # plot avg productivity scores
    if plot_productivity:
        assert(len(r)==len(productivity_dict.values()))
        x = r
        y = [productivity_dict[k] for k in all_unique_keys]
        # print(x)
        # print(y)
        axes2 = plt.twinx()
        axes2.set_ylim(0, max_y)
        axes2.plot(x, y, color='#C72F60', label='Sine')
        for threshold in [3,4,5]:  # dashed line in plot
            axes1.plot([-0.5, len(all_unique_keys) - 0.5], [threshold, threshold], "k--", linewidth=1, color='darksalmon')
        # axes2.plot([-0.5, len(all_unique_keys) - 0.5], [3, 3], "k--", linewidth=1, color='grey')
        axes2.tick_params(axis='y', colors='#C72F60')
        # print(pyplot.yticks())
        pyplot.yticks(np.arange(6), ('',1,2,3,4,5))
        axes2.set_ylabel('Productivity',color='#C72F60')

    # Show graphic
    try:
        plt.show()
    except KeyboardInterrupt:
        pass