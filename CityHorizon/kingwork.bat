@echo off
setlocal enabledelayedexpansion

REM Set marker file path
set "markerFile=%~dp0commit.marker"

REM Get the latest Git commit hash
for /f "delims=" %%H in ('git rev-parse HEAD') do set "latestHash=%%H"

REM Check if marker file exists
if exist "%markerFile%" (
    REM Read the stored hash from the marker file
    set "storedHash="
    for /f "usebackq delims=" %%L in ("%markerFile%") do set "storedHash=%%L"
    
    REM Compare the hashes
    if "!storedHash!"=="!latestHash!" (
        echo Commit hash found. Running normal behavior...
        REM Loop to restart the server if it stops
        :loop1
        echo Starting Django development server...
        start "" python manage.py runserver

        :waitloop1
        timeout /t 2 >nul
        tasklist | findstr /i "python.exe" >nul
        if %ERRORLEVEL%==0 goto waitloop1

        REM After server stops
        cls || clear
        set /p restart="Do you want to restart the server? (y/n): "
        if /i "!restart!"=="y" goto loop1
        exit
    ) else (
        echo New commit detected! Running special behavior...
        REM Navigate to the root of the Django project
        cd /d %~dp0

        REM Activate the virtual environment (if applicable)
        call ..\venv\Scripts\activate

        for /r %%i in (migrations) do (
            for %%f in ("%%i\*initial*.py") do (
                set "appPath=%%i"
                set "appName=!appPath:~3!"
                for %%a in ("!appName!\..") do (
                    set "appName=%%~nxa"
                )
                python manage.py migrate !appName! zero
            )
        )

        echo Unapplied all migrations

        REM Find and delete initial migration files
        for /r %%i in (migrations) do (
            for %%f in ("%%i\*initial*.py") do (
                set "appPath=%%i"
                set "appName=!appPath:~3!"
                for %%a in ("!appName!\..") do (
                    set "appName=%%~nxa"
                )
                del /q "%%f"
                echo Deleted initial migration for !appName!
            )
        )

        echo All initial migration files have been removed.

        REM Run Django makemigrations and migrate
        python manage.py makemigrations
        echo Migrations have been created.

        python manage.py migrate
        echo Migrated to PostgreSQL
        python manage.py create_objects
        python manage.py create_users

        REM Update marker file with new hash
        echo|set /p="!latestHash!" > "%markerFile%"

        REM Loop to restart the server if it stops
        :loop2
        echo Starting Django development server...
        start "" python manage.py runserver

        :waitloop2
        timeout /t 2 >nul
        tasklist | findstr /i "python.exe" >nul
        if %ERRORLEVEL%==0 goto waitloop2

        REM After server stops
        cls || clear
        set /p restart="Do you want to restart the server? (y/n): "
        if /i "!restart!"=="y" goto loop2
        exit
    )
) else (
    echo Marker file not found. First run behavior...
    REM Navigate to the root of the Django project
    cd /d %~dp0

    REM Activate the virtual environment (if applicable)
    call ..\venv\Scripts\activate

    for /r %%i in (migrations) do (
        for %%f in ("%%i\*initial*.py") do (
            set "appPath=%%i"
            set "appName=!appPath:~3!"
            for %%a in ("!appName!\..") do (
                set "appName=%%~nxa"
            )
            python manage.py migrate !appName! zero
        )
    )

    echo Unapplied all migrations

    REM Find and delete initial migration files
    for /r %%i in (migrations) do (
        for %%f in ("%%i\*initial*.py") do (
            set "appPath=%%i"
            set "appName=!appPath:~3!"
            for %%a in ("!appName!\..") do (
                set "appName=%%~nxa"
            )
            del /q "%%f"
            echo Deleted initial migration for !appName!
        )
    )

    echo All initial migration files have been removed.

    REM Run Django makemigrations and migrate
    python manage.py makemigrations
    echo Migrations have been created.

    python manage.py migrate
    echo Migrated to PostgreSQL
    python manage.py create_objects
    python manage.py create_users

    REM Create marker file with current hash
    echo|set /p="!latestHash!" > "%markerFile%"

    REM Loop to restart the server if it stops
    :loop3
    echo Starting Django development server...
    start "" python manage.py runserver

    :waitloop3
    timeout /t 2 >nul
    tasklist | findstr /i "python.exe" >nul
    if %ERRORLEVEL%==0 goto waitloop3

    REM After server stops
    cls || clear
    set /p restart="Do you want to restart the server? (y/n): "
    if /i "!restart!"=="y" goto loop3
    exit
)

endlocal