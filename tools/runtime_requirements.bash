#!/bin/bash

set -e

DATABASE_NAME="Projectdb"
DATABASE_PASSWORD="123"

function start_postgres()
{
    service postgresql start
}

function create_database()
{
    sudo -u postgres psql --command="create database \"$DATABASE_NAME\""
    sudo -u postgres psql --command="grant all privileges on database \"$DATABASE_NAME\" to postgres"
    sudo -u postgres psql --command="ALTER USER postgres WITH PASSWORD '$DATABASE_PASSWORD'"
}

function make_django_migrations()
{
    cd /project/CivicRadar-API
    source .venv/bin/activate
    cd CityHorizon
    ./manage.py makemigrations
    ./manage.py migrate
    deactivate
}

function main()
{
    start_postgres
    create_database
    make_django_migrations
}

main
