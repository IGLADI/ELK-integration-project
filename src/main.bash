# go into the root directory of the project
cd ..

# chmod just in case
chmod +rwx ./src/setup/entrypoint.sh
chmod go-w ./ELK/heartbeat/heartbeat.yml
chmod -R go-w ./ELK/heartbeat/services/
chmod -R 777 ./ELK/elasticsearch/data/

cd src
echo "$PWD"

# just to tell  the user in what mode the script is running
if [[ "${1,,}" == "setup" ]]; then
    echo "Setting up for the first time"

    echo "What version of elasticsearch do you want to use? (current latest is 8.12.2)"
    read ELASTIC_VERSION
    echo "ELASTIC_VERSION=$ELASTIC_VERSION" >.env

    # for now you can't edit the admin username
    echo "ELASTIC_USERNAME='elastic'" >>.env

    echo "What password do you want to use for elasticsearch?"
    read -s ELASTIC_PASSWORD
    echo "ELASTIC_PASSWORD='$ELASTIC_PASSWORD'" >>.env

    echo "What password do you want to use for kibana?"
    read -s KIBANA_SYSTEM_PASSWORD
    echo "KIBANA_SYSTEM_PASSWORD='$KIBANA_SYSTEM_PASSWORD'" >>.env

    echo "What is your rabbitmq username?"
    read RABBITMQ_USERNAME
    echo "RABBITMQ_USERNAME='$RABBITMQ_USERNAME'" >>.env

    echo "What is your rabbitmq password?"
    read -s RABBITMQ_PASSWORD
    echo "RABBITMQ_PASSWORD='$RABBITMQ_PASSWORD'" >>.env

    echo "What is your rabbitmq host?"
    read RABBITMQ_HOST
    echo "RABBITMQ_HOST='$RABBITMQ_PASSWORD'" >>.env

    echo "What is your rabbitmq virtual host?"
    read RABBITMQ_VIRTUAL_HOST
    echo "RABBITMQ_VIRTUAL_HOST='$RABBITMQ_VIRTUAL_HOST'" >>.env

    echo "What is your rabbitmq queue where the heartbeats will be published?"
    read RABBITMQ_QUEUE
    echo "RABBITMQ_QUEUE='$RABBITMQ_QUEUE'" >>.env

    # somtimes buggy when we don't start it before
    docker compose up -d

    # force recreate just in case the network is bugged (due to a previous version)
    docker compose up setup --force-recreate
else
    echo "Starting as normal"
fi

docker compose up -d

echo "Now you can access kibana at http://localhost:16601/app/dashboards#/view/f3e771c0-eb19-11e6-be20-559646f8b9ba?_g=(filters:!(),refreshInterval:(pause:!f,value:1000),time:(from:now-24h%2Fh,to:now))"
echo "Go check out the readme for future steps and setup your first services to monitor"
