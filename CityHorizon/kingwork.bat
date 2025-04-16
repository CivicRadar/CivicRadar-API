@echo off
setlocal enabledelayedexpansion

REM Navigate to the root of the Django project
cd /d %~dp0

REM Activate the virtual environment
call ..\venv\Scripts\activate

REM Unapply all migrations
for /r %%i in (migrations) do (
    for %%f in ("%%i\*initial*.py") do (
        for %%a in ("%%i\..") do (
            set "appName=%%~nxa"
            python manage.py migrate !appName! zero
        )
    )
)
echo Unapplied all migrations

REM Delete initial migration files
for /r %%i in (migrations) do (
    for %%f in ("%%i\*initial*.py") do (
        for %%a in ("%%i\..") do (
            set "appName=%%~nxa"
            del /q "%%f"
            echo Deleted initial migration for !appName!
        )
    )
)
echo All initial migration files have been removed.

REM Delete all folders in the Media directory while preserving files
echo Deleting folders in Media directory...
for /d %%D in (Media\*) do (
    rmdir /s /q "%%D"
    echo Deleted folder: %%D
)
echo All folders in Media directory have been deleted.

REM Create and apply new migrations
python manage.py makemigrations
echo Migrations have been created.
python manage.py migrate
echo Migrated to PostgreSQL

REM Run custom management commands
python manage.py create_objects
python manage.py create_users
python manage.py create_reports