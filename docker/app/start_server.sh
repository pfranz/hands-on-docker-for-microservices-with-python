#!/bin/sh

_term() {
    echo "Caught SIGTERM signal! Sending graceful stop to uWSGI through the master-fifo"
    echo q > /tmp/uwsgi-fifo
}

trap _term SIGTERM

uwsgi --ini /opt/uwsgi/uwsgi.ini &

wait $!

