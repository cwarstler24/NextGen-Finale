FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY docs ./docs
COPY mkdocs.yml ./

EXPOSE 8001

CMD ["mkdocs", "serve", "-a", "0.0.0.0:8001"]
