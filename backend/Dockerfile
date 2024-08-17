FROM python:3.9

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

COPY static/data/fonts/arialmt.ttf /usr/share/fonts/truetype/arialmt.ttf

RUN apt-get update && apt-get install -y fontconfig && \
    fc-cache -f -v

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]