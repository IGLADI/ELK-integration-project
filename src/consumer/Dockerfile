FROM python:3.8-slim

WORKDIR /app

# the csv is a volume, so we don't need to copy it here
COPY ./consumer.py ./consumer.py
COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

# get log outputs
ENV PYTHONUNBUFFERED=1

CMD ["python", "consumer.py"]