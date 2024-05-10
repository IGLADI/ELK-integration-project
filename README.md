# ELK Controlroom Integration Project

![Dashboard](./screenshots/dashboard.png)

## Tech stack

-   Docker
-   ELK stack
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

Before running any of the next commands, please make sure you're in the `/monitoring/Monitoring/src` folder (or similar if you have placed the project somewhere else) with the following command:

```bash
cd /monitoring/Monitoring/src
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

For the manual install guide, please click [here](manual_install.md).

## Adding services to monitor

### Heartbeat monitoring

If you'd like to add a service to monitor, please follow these steps:

Considering you're still in the `./src` folder, run:

```bash
cd ./consumer
```

After that, you'll be able to edit the csv with a list of service names you want to monitor.

```bash
nano ./heartbeat_rabbitmq.csv
```

**Notes**

-   We check for new csv file every minute, consider it may take up to 30 seconds (with both the dashboard and the service set to reload every second) before showing up.

#### Heartbeat configuration

We expect the services to monitor to push the following [XSD format](./template.xsd) to the queue.

## Troubleshooting

### Fixing permissions

You may need to run the following to fix some permission issues depending on your platform (in the home folder, not src folder):

```bash
chmod +rwx ./src/setup/entrypoint.sh
chmod -R 777 ./ELK/elasticsearch/data/
```

**Note** the last chmod recursively adds all permissions to everyone. If this is set on a real server with untrusted users, please change this to only give the required permissions.

### Restart from scratch

If you wish to restart from scratch you can:

go into the `./src` folder and run the following command:

```bash
sudo bash ./main.bash down
```

And then delete the volumes with the following command:

```bash
sudo rm -rf ../ELK/elasticsearch/data/
```

Now you will only need to change any config file you have changed (like `heartbeat_rabbitmq.csv` or the `export.ndjson`) and run the setup:

```bash
sudo bash ./main.bash setup
```

**Note** If you really want to reset everything from scratch including any config files you've changed, you can delete the repo and clone it again (make sure to backup any important files and that everything is down before processing).

### Reverse-proxy

If you're using a reverse proxy, keep in mind it should still be on the same network. You could create a new one and add Kibana to it if you wish to do so (if you do end up using one, port 16601 is used for the web interface, feel free to unassign it inside `./src/docker-compose.yml` if you use a reverse proxy). Inside the reverse proxy, point it towards this destination: `http://kibana:5601/`.

### First-time loading issues web UI

Whilst the service is starting up, you may have issues whilst loading the web interface, with random issues popping up that aren't related to what you're doing. To counter this, wait about a minute, then refresh your page.

**Note**

-   You may also want to check [tests](README.md#Tests), or check the container logs with `docker logs <container_id>`.
-   If you wish to access more website tips, please click [here](website_utils.md).

## Tests

### Run all tests at once

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
