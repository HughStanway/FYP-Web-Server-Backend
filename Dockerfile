FROM python:3.12

ENV VOYAGE_API_KEY=pa-TxEv8WHHYb0aW_sb1hFoIUp7uLnldoR8esBXqs_lHDT

RUN apt update && apt install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt install -y nodejs

RUN node -v
RUN npm -v
RUN npx --version

RUN npm install -g prettier prettier-plugin-java
RUN prettier --version

WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
