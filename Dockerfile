FROM python:3.12

ENV COLLECTION_NAME=FypPrototypeCollection
ENV VOYAGE_API_KEY=pa-TxEv8WHHYb0aW_sb1hFoIUp7uLnldoR8esBXqs_lHDT

WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
