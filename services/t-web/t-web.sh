#!/bin/sh
# certbot renewal hook. Put this in /etc/letsencrypt/renewal-hooks/post
exec systemctl restart t-web.service
