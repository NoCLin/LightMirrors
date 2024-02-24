#!/usr/bin/env sh
touch /data/aria2.session

aria2c --conf-path=/aria2.conf --rpc-secret $RPC_SECRET