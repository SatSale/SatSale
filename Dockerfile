FROM python:3.8 

WORKDIR /build
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
#USER 1000
#WORKDIR /build
#COPY --from=builder /build .
#EXPOSE 3002


CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:8000", "satsale:app"]

EXPOSE 8000
EXPOSE 22
