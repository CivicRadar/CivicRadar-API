#!/bin/bash

DATABASE_NAME="Projectdb"
DATABASE_PASSWORD="123"

set -e

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

function main()
{
    start_postgres
    create_database
}

main
