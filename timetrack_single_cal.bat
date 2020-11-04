@echo OFF
SET TIMETRACKDIR=\Users\nicole\code\timetrack
SET PREVDIR=%CD%

:timetrack_single_cal
CALL cd %TIMETRACKDIR%
CALL python src\single_calendar.py %*
CALL cd %PREVDIR%
PAUSE
EXIT /B 0
