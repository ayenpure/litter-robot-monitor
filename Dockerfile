FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY litter_monitor/ litter_monitor/
COPY main.py .

RUN useradd --create-home --uid 1000 monitor \
    && mkdir -p /app/data \
    && chown -R monitor:monitor /app
USER monitor

CMD ["python", "main.py"]
