set scriptpath=%~dp0
cd %scriptpath%
call %HOMEDRIVE%%HOMEPATH%\anaconda3\Scripts\activate.bat
python -u main.py