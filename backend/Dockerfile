FROM python:3.14
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /usr/local/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic ./alembic
COPY alembic.ini run.py ./
COPY app ./app
EXPOSE 8000

RUN useradd api
USER api

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
