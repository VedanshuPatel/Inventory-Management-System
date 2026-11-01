FROM python:3.12.10-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV INVENTORY_DB=/data/inventory.db

CMD ["python", "main.py"]