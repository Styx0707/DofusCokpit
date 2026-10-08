FROM python:3.11-slim

# Scapy s'appuie sur libpcap pour la capture ; tcpdump aide au diagnostic.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpcap0.8 tcpdump \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY sql ./sql
COPY scripts ./scripts
COPY data ./data

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/srv

CMD ["python", "-m", "app.main"]
