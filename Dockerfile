FROM node:16-bullseye-slim AS assets
WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && mkdir -p /node_modules && chown node:node -R /node_modules /app

USER node
COPY --chown=node:node app/package.json ./

RUN npm install

ARG NODE_ENV="production"
ENV NODE_ENV="${NODE_ENV}" \
    PATH="${PATH}:/node_modules/.bin" \
    USER="node"

COPY --chown=node:node app /app

RUN npx tailwindcss --minify -i /app/static/src/style.css -o /app/static/css/main.css

CMD ["bash"]

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
COPY app ./
COPY --from=assets /app/static/css/main.css /app/static/css/main.css
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
