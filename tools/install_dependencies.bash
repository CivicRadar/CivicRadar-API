#!/bin/bash

set -e

function install_postgres()
{
    apt install -y postgresql-common
    /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh 
    apt install postgresql-17 postgresql-client-17 -y
}

function install_python()
{
    apt install -qy python3 python3-pip python3.12-venv
}

function main()
{
    apt update -y
    apt upgrade -y
    install_postgres
    install_python
}

main
