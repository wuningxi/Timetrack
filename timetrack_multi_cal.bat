@echo OFF
SET TIMETRACKDIR=\Users\nicole\code\timetrack
SET PREVDIR=%CD%

:timetrack_multi_cal
CALL cd %TIMETRACKDIR%
CALL python src\multi_calendar.py %*
CALL cd %PREVDIR%
PAUSE
EXIT /B 0
