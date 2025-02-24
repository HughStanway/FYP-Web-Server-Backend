FROM python:3.12

ENV VOYAGE_API_KEY=pa-

WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
