FROM python:3.8-slim

WORKDIR /app

# the csv is a volume, so we don't need to copy it here
COPY ./export_setup.py ./export_setup.py
COPY ./requirements.txt ./requirements.txt
COPY ./export.ndjson ./export.ndjson

RUN pip install -r ./requirements.txt

# get log outputs
ENV PYTHONUNBUFFERED=1

CMD ["python", "export_setup.py"]