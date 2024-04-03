FROM python:3.8-slim

WORKDIR /app

COPY ./consumer.py ./consumer.py
COPY ./requirements.txt ./requirements.txt
COPY ./.env ./.env

RUN pip install -r ./requirements.txt

# get log outputs
ENV PYTHONUNBUFFERED=1

CMD ["python", "consumer.py"]