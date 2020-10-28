#!/bin/bash

export TIMETRACKDIR=/path/to/timetrack # e.g. Users/nicole/code/timetrack

function timetrack_multi_cal() {
        # switch to timetrack dir
        cd $TIMETRACKDIR
        python src/multi_calendar.py $@
        # switch back to original dir
        cd -
}

function timetrack_single_cal() {
        cd $TIMETRACKDIR
        python src/single_calendar.py $@
        # switch back to original dir
        cd -
}
