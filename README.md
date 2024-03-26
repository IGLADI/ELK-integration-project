# ELK Stack integration project

Links of used resources: <https://github.com/Jardelpz/events_savior?tab=readme-ov-file> and <https://github.com/deviantony/docker-elk/tree/main?tab=readme-ov-file#host-setup> should be mentionned in README.md ASAP

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

To start ELK run:

```bash
docker compose up setup
```

& then:

```bash
docker compose up -d
```
