# ELK Controlroom Integration Project

![Dashboard](./screenshots/dashboard.png)

## Tech stack

-   Docker
-   ELK
-   Heartbeat (http monitoring for redundancy + may help with debugging)
-   Python
-   RabbitMQ
-   Bash/Shell scripting

## Disclaimer

To run our project, we're making the assumption you're on linux and have Docker installed. If you're on windows, you can use WSL.

## TL;DR

### Script

Before running the script, make sure you have a RabbitMQ instance running. If this isn't running yet, you can run the following command:

```bash
docker compose -f ./extra/rabbitmq_general_team/docker-compose.yml up -d
```

Before running any of the next commands, please make sure you're in the `src` folder with the following command:

```bash
cd src
```

To setup the service for the first time, run the following command:

```bash
sudo bash ./main.bash setup
```

To stop the service, run the following command:

```bash
sudo bash ./main.bash stop
```

To simply start the service, run the following command:

```bash
sudo bash ./main.bash
```

### Manual installation

Before running the script, make sure you have a RabbitMQ instance running. If this isn't running yet, you can run the following command:

```bash
docker compose -f ./extra/rabbitmq_general_team/docker-compose.yml up -d
```

Go into the `./src` folder:

```bash
cd src
```

Create a `.env` file based on the `.env.example` file inside the `./src` folder and **fill in the required fields**.

```bash
cp ./.env.example ./.env
```

To start ELK for the first time, run:

```bash
docker compose up setup --force-recreate
```

**Note:** this should only be ran once.

After the setup is done, you can run the ELK stack with the following command (this means you'll never need to run the setup script again, and you'll only need to run this command from this point onwards):

```bash
docker compose up -d
```

You can now access the dashboard via <http://localhost:16601/app/dashboards#/view/f3e771c0-eb19-11e6-be20-559646f8b9ba?_g=(filters:!(),refreshInterval:(pause:!f,value:1000),time:(from:now-24h%2Fh,to:now))>

After clicking the link, enter your login credentials to be redirected to the monitoring dashboard. The default username is `elastic` (will be modifiable in .env), and the password is what you've entered in the `KIBANA_SYSTEM_PASSWORD` variable in your `./src/.env` file.

**Note:** replace localhost with your local IP.

If you wish to stop the service, run the following command:

```bash
docker compose down
```

## Adding services to monitor

### Heartbeat monitoring

If you'd like to add a service to monitor, please follow these steps:

Considering you're still in the `./src` folder, run:

```bash
cd ../ELK/heartbeat/services
```

Create a `service.yml.unconfirmed` file based on the `template.yml.unconfirmed` file inside the `./ELK/heartbeat/services` folder with this command:

```bash
cp ./template.yml.unconfirmed ./service.yml.unconfirmed
```

Once filled in correctly, modify the name accordingly (modify `service` to the actual name of the service):

```bash
mv ./service.yml.unconfirmed ./service.yml
```

**Notes**

-   We check for new yaml files every 5 seconds, consider it may take up to 10 seconds (with both the dashboard and the service set to reload every second) before showing up.
-   We also update the consumer with the csv file every minute, so it may take up to 1.5 minutes before the service is fully operational.
-   While a yml file isn't configured properly, we recommend to keep the `.unconfirmed` extension.
-   If you temporarily don't want to monitor a service you can set `enabled: false` in the yaml file.

#### Heartbeat configuration

We expect the services to monitor to push the following [XSD format](./template.xsd) to the queue.

## Troubleshooting

### Fixing permissions

You may need to run the following to fix some permission issues depending on your platform (in the home folder, not src folder):

```bash
chmod +rwx ./src/setup/entrypoint.sh
chmod go-w ./ELK/heartbeat/heartbeat.yml
chmod -R go-w ./ELK/heartbeat/services/
chmod -R 777 ./ELK/elasticsearch/data/
```

**Note** the last chmod recursively adds all permissions to everyone. If this is set on a real server with untrusted users, please change this to only give the required permissions.

### Reverse-proxy

If you're using a reverse proxy, keep in mind it should still be on the same network. You could create a new one and add Kibana to it if you wish to do so (if you do end up using one, port 16601 is used for the web interface, feel free to unassign it inside `./src/docker-compose.yml` if you use a reverse proxy). Inside the reverse proxy, point it towards this destination: `http://kibana:5601/`.

### First-time loading issues web UI

Whilst the service is starting up, you may have issues whilst loading the web interface, with random issues popping up that aren't related to what you're doing. To counter this, wait about a minute, then refresh your page.

**Note**

-   You may also want to check [tests](README.md#Tests), or check the container logs with `docker logs <container_id>`.
-   If you wish to access more website tips, please click [here](website_utils.md).

## Tests

### run all tests at once

If you'd like to verify everything at once, there's a few steps to follow.

You'll first need to enter `./src`. To do so, type this in your console:

```bash
cd ./src
```

After that, you'll need to run the `tests-script.bash` file. To do this, execute the following command in your CLI:

```bash
sudo bash ./tests-script.bash
```

### Run tests individually

#### docker-compose validation

In case you'd like to verify the integrity of the `docker-compose.yml` file, follow the steps below.

If you've never done a docker-compose test, please execute the following command first:

```bash
sudo apt install docker-compose
```

**Note** your packet manager may differ.

Once docker-compose is installed, please run the following command. If the file is good to go, it should return "OK". Else, it'll return "ERROR":

```bash
docker-compose config --quiet && printf "OK\n" || printf "ERROR\n"
```

#### yaml validation

First off, make sure the project is running. If it isn't running, please do so [here](README.md#Setup).

Secondly, you'll need to enter the container. To do so, there's a few steps to follow.

Get the required information of the container with the following command:

```bash
sudo docker container ls | grep heartbeat
```

Now, look for the container running heartbeat. Use the ID for the following command:

```bash
sudo docker exec -it <id> bash
```

Inside the container, you can validate the content of the yaml file with the commands written below.

To validate the content of the yaml, enter the following command:

```bash
./heartbeat test config -c ~/heartbeat.yml --path.data ~/data/ --path.home ~
```

If there are any errors and you'd like to see a more detailed explanation of what's good and wrong, use this command:

```bash
./heartbeat test output -c ~/heartbeat.yml --path.data ~/data/ --path.home ~
```

Once finished, exit the container with the following command:

```bash
exit
```

## Used ports (assigned range:16000-23999)

-   5672 (RabbitMQ api)
-   15672 (RabbitMQ frontend)
-   16000 (Portainer, this would typically be 8000)
-   16601 (Kibana, this would typically be 5601)
-   19200 (Elasticsearch API, this would typically be 9200)
-   19300 (Elasticsearch binary protocol, this would typically be 9300)
-   17443 (Portainer https front-end, this would typically be 9443)

**Note**
RabbitMQ doesn't follow the assigned ranges as it's for the general group (can be run from outside) and people were already publishing to those ports.

## Used/interesting resources

-   [Official ELK docs](https://www.elastic.co/guide/index.html)
-   [Heartbeat installation configuration](https://www.elastic.co/guide/en/beats/heartbeat/current/heartbeat-installation-configuration.html)
-   [RabbitMQ training course](https://training.cloudamqp.com/)
-   No code used but pretty interesting to read: [check them out](https://github.com/Jardelpz/events_savior?tab=readme-ov-file)
-   [Used repo 1](https://github.com/deviantony/docker-elk) setup script and also inspiration from reading their code base **FOLLOW THEIR [MIT LICENSE](https://github.com/deviantony/docker-elk/blob/main/LICENSE)!** or [BACKUP LINK](./MIT_LICENSE.txt)
-   [Used repo 2](https://github.com/elastic/uptime-contrib) dashboard resources used form their 7.x dashboard **FOLLOW THEIR [APACHE LICENSE](https://github.com/elastic/uptime-contrib/blob/master/LICENSE)!** or [BACKUP LINK](./APACHE_LICENSSE.txt)
-   [YTB NetworkChuck tutorial docker](https://www.youtube.com/watch?v=eGz9DS-aIeY)
-   [YTB NetworkChuck tutorial docker compose](https://www.youtube.com/watch?v=DM65_JyGxCo)
-   [YTB IBM message queue](https://www.youtube.com/watch?v=xErwDaOc-Gs)
-   [YTB IBM RabbitMQ](https://www.youtube.com/watch?v=7rkeORD4jSw)
-   [YTB ELK tutorial 1 part 1](https://www.youtube.com/watch?v=MB94whqmSKI) & [YTB ELK guide 1 part 2](https://www.youtube.com/watch?v=JcGIFmkg1bE)
-   [YTB ELK tutorial 2 (french)](https://www.youtube.com/watch?v=S5MyeD8ysxA)
