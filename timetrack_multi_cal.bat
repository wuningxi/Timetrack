@echo OFF
SET %TIMETRACKDIR=\Users\nicole\code\timetrack

:timetrack_multi_cal
CALL cd %TIMETRACKDIR%
ECHO %CD%
CALL python src\multi_calendar.py %*
PAUSE
EXIT /B 0
