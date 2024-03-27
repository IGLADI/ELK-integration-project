# ELK Stack integration project

Links of used resources: <https://www.elastic.co/guide/index.html> and <https://github.com/Jardelpz/events_savior?tab=readme-ov-file> and <https://github.com/deviantony/docker-elk/tree/main>

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

& then:

```bash
docker compose up -d
```

you may need to run

```bash
chmod +rwx ./setup/entrypoint.sh
chmod go-w ./heartbeat/heartbeat.yml
```

If an error occurs due to the network try running:

```bash
docker compose up setup --force-recreate
```
