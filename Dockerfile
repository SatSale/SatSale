FROM python:3.8

WORKDIR /build
#COPY requirements.txt .

ADD requirements.txt /build
RUN pip3 install -r requirements.txt

#USER 1000
#WORKDIR /build
#COPY --from=builder /build .
#EXPOSE 3002

#USER 1000

EXPOSE 8000

#CMD ["ping", "172.17.0.1"]
#CMD ["curl", "--data-binary", "{'jsonrpc':'1.0','id':'curltext','method':'getblockchaininfo','params':[]}", "-H", "content-type:text/plain;", "http://bitcoinrpc:16Lrxm3npTeJAAAA2pd6d9uFjgHVYzwQg4@172.17.0.1:7332/"]
ENV PYTHONUNBUFFERED 1
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:8000", "satsale:app"]
