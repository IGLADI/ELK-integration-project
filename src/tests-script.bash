returnvalue=0

cd src || echo "already in src"
if [ ! -f "./.env" ]; then
    sudo bash ./main.bash setup 8.12.2 pwd pwd guest guest 127.0.0.1 / heartbeat_queue
fi

# install docker compose in case this isn't ready yet
sudo apt update
sudo apt install docker-compose -y
# check the docker-compose config
docker-compose config --quiet && docker_compose="Docker-compose OK" || docker_compose="\033[0;31mDocker-compose ERROR\033[0m"
if [ "$docker_compose" != "Docker-compose OK" ]; then
    returnvalue=1
fi

# get the container id
container_info=$(sudo docker container ls | grep "heartbeat")
container_id=$(echo "$container_info" | awk '{print $1}')

# enter the container for test & print both test results
printf "\n\n\nVALIDATION \n$docker_compose\n"

echo "Waiting for container to be started"
until [ "$(docker inspect -f {{.State.Running}} heartbeat)"=="true" ]; do
    sleep 0.1
done

# run yaml config test
printf "HEARTBEAT\n" && output=$(sudo docker exec $container_id bash -c '~/heartbeat test config -c ~/heartbeat.yml --path.data ~/data/ --path.home ~ && exit' | tail -n 1)

# strip white spaces around "config ok"
output="${output#"${output%%[![:space:]]*}"}"
output="${output%"${output##*[![:space:]]}"}"
echo $output

if [ "$output" != "Config OK" ]; then
    returnvalue=1
    echo "\033[0;31mHEARTBEAT CONFIG FAILED\033[0m"
fi

bash ./main.bash down

exit $returnvalue
