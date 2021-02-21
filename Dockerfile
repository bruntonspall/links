FROM python:3.7.2-slim-stretch as build

COPY . /links

RUN pip install /links

FROM python:3.7.2-slim-stretch

# Copy python dependencies and spatialite libraries
COPY --from=build /usr/local/lib/ /usr/local/lib/
# Copy executables
COPY --from=build /usr/local/bin /usr/local/bin

EXPOSE 8001
CMD ["links"]
