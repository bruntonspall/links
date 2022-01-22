FROM python:3.10-slim as build

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY app ./

ENV GOOGLE_APPLICATION_CREDENTIALS=/config
RUN pytest

FROM python:3.10-slim
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY --from=build /app .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
