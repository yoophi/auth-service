#!/bin/sh

exec gunicorn -b :5000 --access-logfile - --error-logfile - wsgi:app
