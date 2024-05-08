#!/bin/bash

cd src || echo "already in src"

if [ ! -f "./.env" ]; then
    # if you have an env we assume you have rabbitmq running
    docker-compose -f ../extra/rabbitmq_general_team/docker-compose.yml up -d
    sudo bash ./main.bash setup 8.12.2 pwd pwd guest guest 127.0.0.1 / heartbeat_queue
else
    sudo bash ./main.bash
fi

# install docker compose in case this isn't ready yet
sudo apt update
sudo apt install docker-compose -y
# check the docker-compose config
docker-compose config --quiet || exit 1
