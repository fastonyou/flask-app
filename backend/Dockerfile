FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*



WORKDIR /app 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
