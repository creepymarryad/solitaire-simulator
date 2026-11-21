@echo off
chcp 65001 >nul
cls

:MENU
echo ========================================
echo           SYMULATOR PASJANSA
echo ========================================
echo.
echo  [1] Start
echo  [2] Koniec
echo.
set /p wybor="Twoj wybor: "

if "%wybor%"=="1" goto RUN_ALL
if "%wybor%"=="2" exit

goto MENU

:RUN_ALL
cls
echo [INFO] Uruchamianie obliczen...
python main.py --batch

if %errorlevel% neq 0 goto ERROR_PYTHON

echo.
echo [SUKCES] Obliczenia zakonczone.
echo Otwieranie raportu...
start "" "out\raport.html"
echo.

if not exist out\replay.pkl goto NO_REPLAY

echo Znaleziono wygrane partie.
set /p show_anim="Uruchomic wizualizacje? (t/n): "

if /i "%show_anim%"=="t" python main.py --replay

goto MENU

:NO_REPLAY
echo.
echo Brak wygranych partii (lub same porazki)
echo Wizualizacja niedostepna
pause
goto MENU

:ERROR_PYTHON
echo.
echo [BLAD KRYTYCZNY] Program Python zakonczyl sie bledem
pause
goto MENU