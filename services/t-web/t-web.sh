#!/bin/bash
# certbot renewal deploy hook. Put this in /etc/letsencrypt/renewal-hooks/deploy

set -exu

tmpdir=$(mktemp -d)
all_pem=$tmpdir/all.pem
trap "rm -rf '$tmpdir'" EXIT

cat /etc/letsencrypt/live/twistedmatrix.com/privkey.pem /etc/letsencrypt/live/twistedmatrix.com/fullchain.pem > "$all_pem"

install -m 0644 -o t-web -g www-data "$all_pem" /srv/t-web/ssl/twistedmatrix.com.pem
install -m 0644 -o t-web -g www-data "$all_pem" /srv/t-web/ssl/www.twistedmatrix.com.pem

systemctl restart t-web.service
