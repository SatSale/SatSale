#!/bin/bash

lnd_network=regtest

. /usr/share/lnd/lib/bash.sh

cat <<EOF > config.toml
pay_method = "lnd"
lnd_rpcport = "$lnd_grpc_port"
lnd_macaroon = "$lnd_invoice_macaroon_file"
lnd_cert = "$lnd_cert_file"
EOF
