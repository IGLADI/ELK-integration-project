FROM python:3.8-slim

WORKDIR /app

# the csv is a volume, so we don't need to copy it here
COPY ./consumer.py ./consumer.py
COPY ./requirements.txt ./requirements.txt
# not needed when we don't do xml validation
# COPY ./template.xsd ./template.xsd
# COPY ./xmlxsd/main.xsd ./main.xsd

RUN pip install -r ./requirements.txt

# get log outputs
ENV PYTHONUNBUFFERED=1

CMD ["python", "consumer.py"]