FROM python:3.11-slim

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ExPOSE 8000

CMD ["python", "main.py"]