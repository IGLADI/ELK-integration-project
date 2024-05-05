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