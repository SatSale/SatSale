FROM python:3.8

WORKDIR /build
RUN mkdir /build/lnd
COPY --chown=1000:1000 . .

RUN pip3 install -r requirements.txt

USER 1000

EXPOSE 8000
EXPOSE 5000

ENV PYTHONUNBUFFERED 1
CMD ["gunicorn", "--worker-class", "eventlet", "--bind", "0.0.0.0:5000", "-w", "1", "satsale:app"]
