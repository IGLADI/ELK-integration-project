# ELK Stack integration project

Links of used resources: <https://www.elastic.co/guide/index.html> and <https://github.com/Jardelpz/events_savior?tab=readme-ov-file> and <https://github.com/deviantony/docker-elk/tree/main> and <https://github.com/elastic/uptime-contrib>

<!-- old version:
to setup ELK: Setup keys via:
docker exec -it <elastic_id> bash
cd bin
elasticsearch-create-enrollment-token --scope kibana
copy paste the token into the webui

docker exec -it <kibana_id> bash
cd bin
./kibana-verification-code
copy paste the verification code into the webui -->

To start ELK run (keep in mind the reverse proxy should be in a network named `cloud`):

```bash
docker compose up setup
```

Note that this should be run only once.

If an error occurs due to the network try running this instead:

```bash
docker compose up setup --force-recreate
```

After the setup is done you can run the ELK stack with:

```bash
docker compose up -d
```

You may need to run the following to fix some permission issues:

```bash
chmod +rwx ./setup/entrypoint.sh
chmod go-w ./heartbeat/heartbeat.yml
```

Then you need to import `export.ndjson` into `Saved Objects` and you should see the dashboard appear in kibana.
