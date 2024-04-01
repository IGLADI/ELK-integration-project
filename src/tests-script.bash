# install docker compose in case this isn't ready yet
sudo apt install docker-compose -y

# check the docker-compose config
docker-compose config --quiet && docker_compose="Docker-compose OK" || docker_compose="Docker-compose ERROR"

# shut down active container & start new one 
sudo docker compose up -d

# get the container id
container_info=$(sudo docker container ls | grep "heartbeat")
container_id=$(echo "$container_info" | awk '{print $1}')

# enter the container for test & print both test results
printf "\n\n\nVALIDATION \n$docker_compose\n"
printf "HEARTBEAT\n" && sudo docker exec -it $container_id bash -c '~/heartbeat test config -c ~/heartbeat.yml --path.data ~/data/ --path.home ~ && exit'
