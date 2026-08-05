FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY model_cleaning .

EXPOSE 5001

CMD ["python", "cleaning.py"]