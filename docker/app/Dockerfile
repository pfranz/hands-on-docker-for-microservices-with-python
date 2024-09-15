FROM alpine:3.20.3 AS compile-image

RUN apk add --update python3

RUN mkdir -p /opt/code
WORKDIR /opt/code

RUN apk add python3-dev build-base gcc linux-headers postgresql-dev libffi-dev cargo

# Create a virtual environment for all the Python dependencies
RUN python3 -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
RUN pip3 install --upgrade pip

# Install and compile uwsgi
RUN pip3 install uwsgi==2.0.24
# Install other dependencies
COPY ThoughtsBackend/requirements.txt /opt/
RUN pip3 install -r /opt/requirements.txt


FROM alpine:3.20.3 AS runtime-image

RUN apk add --update python3 curl libffi postgresql-libs

RUN mkdir -p /opt/uwsgi
ADD docker/app/uwsgi.ini /opt/uwsgi/
ADD docker/app/start_server.sh /opt/uwsgi/

RUN addgroup -S uwsgi
RUN adduser -H -D -S uwsgi
USER uwsgi

COPY --chown=uwsgi:uwsgi --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=uwsgi:uwsgi ThoughtsBackend/ /opt/code/

WORKDIR /opt/code
EXPOSE 8000
CMD ["/bin/sh", "/opt/uwsgi/start_server.sh"]
