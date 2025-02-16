FROM python:3.10

WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/app.py .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
