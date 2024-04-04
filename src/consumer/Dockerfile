FROM python:3.8-slim

WORKDIR /app

COPY . .

RUN pip install -r ./requirements.txt

# get log outputs
ENV PYTHONUNBUFFERED=1

CMD ["python", "consumer.py"]