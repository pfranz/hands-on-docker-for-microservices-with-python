FROM alpine

ARG POSTGRES_DB
ENV POSTGRES_DB $POSTGRES_DB
ARG POSTGRES_USER
ENV POSTGRES_USER $POSTGRES_USER
ARG POSTGRES_PASSWORD
ENV POSTGRES_PASSWORD $POSTGRES_PASSWORD
ARG POSTGRES_PORT
ENV LANG en_US.utf8
EXPOSE $POSTGRES_PORT

ENV POSTGRES_HOST localhost
ENV DATABASE_ENGINE POSTGRESQL

RUN mkdir -p /opt/data
ENV PGDATA /opt/data


RUN apk update
RUN apk add bash curl su-exec python3 py3-pip
RUN apk add postgresql postgresql-contrib postgresql-dev
RUN apk add python3-dev build-base linux-headers gcc libffi-dev


WORKDIR /opt/code

RUN mkdir -p /opt/code/db
# Add postgres setup
ADD ./docker/db/postgres-setup.sh /opt/code/db/
RUN /opt/code/db/postgres-setup.sh

## Install our code prepare DB
ADD ./ThoughtsBackend/requirements.txt /opt/code

RUN pip3 install -r requirements.txt --break-system-packages

## Need to import all the code, due to dependencies to initialized the DB
ADD ./ThoughtsBackend/ /opt/code/
# Add all the DB commands
ADD ./docker/db/* /opt/code/db/

# get the db ready
RUN /opt/code/db/prepare_db.sh

# Start the database in normal operation
USER postgres
CMD ["postgres"]
