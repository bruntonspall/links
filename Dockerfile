FROM python:3.7 as build

COPY . .
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

# RUN pytest .

FROM python:3.7-slim
COPY --from=build app /app
COPY --from=build requirements.txt /app

WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python", "main.py"]
