@echo OFF
SET %TIMETRACKDIR=\Users\nicole\code\timetrack

:timetrack_single_cal
CALL cd %TIMETRACKDIR%
ECHO %CD%
CALL python src\single_calendar.py %*
PAUSE
EXIT /B 0
