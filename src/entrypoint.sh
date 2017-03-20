#!/bin/bash
set -e

nginx
exec ./run.py $1 $NGINX_HTML


