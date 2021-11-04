FROM python:3.8

WORKDIR /build
#RUN mkdir /build/lnd
COPY --chown=1000:1000 . .

RUN pip3 install -r requirements.txt

USER 1000
EXPOSE 5000

ENV PYTHONUNBUFFERED 1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-w", "1", "satsale:app"]
#CMD ["gunicorn", "--worker-class", "eventlet", "--bind", "0.0.0.0:5000", "-w", "1", "satsale:app"]


#### need
# Probably need a volume to store the API key file into
# Probably need webstore branch (needs rebase) by default?
# Versioning?
#
