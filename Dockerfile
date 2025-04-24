FROM ubuntu:noble
# mapping ports

ARG GIT_BRANCH=main

# postgresql
EXPOSE 5432

# python server
EXPOSE 8000

RUN apt update -y && apt upgrade -y

RUN apt install -y iproute2 curl unzip

WORKDIR /install_dependencies

COPY tools/install_dependencies.bash .

WORKDIR /project

RUN git clone --branch $GIT_BRANCH https://github.com/CivicRadar/CivicRadar-API.git

WORKDIR /project/CivicRadar-API

RUN python3 -m venv .venv

RUN bash -c "source .venv/bin/activate && pip install -r CityHorizon/requirements.txt"

