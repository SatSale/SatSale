#!/bin/bash

set -e

# WARNING: RUN IN DEBIAN 10 VM WITH PASSWORDLESS SUDO!!!
#
# This script tests BTCPyment on regtest using lnpbp_testkit, selenium, and cryptoanarchy deb repository
# Run from project root

gpg --keyserver hkp://keyserver.ubuntu.com --recv-keys 3D9E81D3CA76CDCBE768C4B4DC6B4F8E60B8CF4C
gpg --keyserver hkp://keyserver.ubuntu.com --recv-keys BC528686B50D79E339D3721CEB3E94ADBE1229CF
gpg --export 3D9E81D3CA76CDCBE768C4B4DC6B4F8E60B8CF4C | sudo apt-key add -
gpg --export BC528686B50D79E339D3721CEB3E94ADBE1229CF | sudo apt-key add -
echo 'deb [arch=amd64,arm64,armhf] https://packages.microsoft.com/debian/10/prod buster main' | sudo tee /etc/apt/sources.list.d/microsoft.list > /dev/null
echo 'deb [signed-by=3D9E81D3CA76CDCBE768C4B4DC6B4F8E60B8CF4C] https://deb.ln-ask.me/beta buster common local desktop' | sudo tee /etc/apt/sources.list.d/cryptoanarchy.list > /dev/null
sudo apt update

# Installing python libraries via apt is much, much faster
sudo apt install -y bitcoin-regtest lnd python3-lnpbp-testkit python3-selenium python3-grpcio python3-grpc-tools python3-toml python3-qrcode python3-flask python3-markupsafe python3-requests python3-gunicorn python3-eventlet python3-protobuf
pip3 install -r requirements.txt
sudo usermod -a -G lnd-system-regtest-invoice "$USER"

# Trick to apply new permissions without logging out and in
sudo -u $USER ./tests/init_config.sh
sudo -u $USER python3 server.py &
sleep 5
XDG_RUNTIME_DIR=/run/user/$(id -u $USER) python3 ./tests/lightning.py
