FROM yoophi/python-psycopg2-pycryptodome:3.7.7-alpine3.12

ENV FLASK_APP wsgi.py
ENV FLASK_CONFIG production

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements /requirements

COPY . .
RUN python setup.py install
RUN pip install -r /requirements/prod.txt

COPY wsgi.py ./
COPY docker/entrypoint.sh ./


EXPOSE 5000
ENTRYPOINT ["./entrypoint.sh"]
