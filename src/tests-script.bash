returnvalue=0

cd src || echo "already in src"
if [ ! -f "./.env" ]; then
    sudo bash ./main.bash setup 8.12.2 pwd pwd guest guest 10.2.160.15 / heartbeat_queue
fi

# install docker compose in case this isn't ready yet
sudo apt install docker-compose -y
# check the docker-compose config
docker-compose config --quiet && docker_compose="Docker-compose OK" || docker_compose="Docker-compose ERROR"
if [ "$docker_compose" != "Docker-compose OK" ]; then
    returnvalue=1
fi
# shut down active container & start new one
sudo docker compose up -d

# get the container id
container_info=$(sudo docker container ls | grep "heartbeat")
container_id=$(echo "$container_info" | awk '{print $1}')

# enter the container for test & print both test results
printf "\n\n\nVALIDATION \n$docker_compose\n"
# wait for the container to be started
until [ "`docker inspect -f {{.State.Running}} heartbeat`"=="true" ]; do
    sleep 0.1;
done;
# make sure the container is healthy
sleep 1m
printf "HEARTBEAT\n" && output=$(sudo docker exec $container_id bash -c '~/heartbeat test config -c ~/heartbeat.yml --path.data ~/data/ --path.home ~ && exit' | tail -n 1)

# strip space around "config ok"
output="${output#"${output%%[![:space:]]*}"}"
output="${output%"${output##*[![:space:]]}"}"
echo $output

if [ "$output" != "Config OK" ]; then 
    returnvalue=1
fi

bash ./main.bash down

exit $returnvalue
