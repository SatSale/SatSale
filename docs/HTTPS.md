## Using a Subdomain with nginx & certbot (HTTPS)
Embedded iframes are easy if your site only uses HTTP. But if your site uses HTTPS, then you can likely see your donation button at `http://YOUR_SERVER_IP:8000/` but not in the embeded iframe. It is best that we create a new subdomain like `satsale.yoursite.com` from which we can serve payments. If you use nginx, you can create a new file `/etc/nginx/sites-enabled/satsale`:
```
server {
    listen 80;
    server_name satsale.YOURWEBSITE.com;

    location / {
        proxy_pass http://localhost:8000;
	proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```
we can now point our domain `satsale.YOURWEBSITE.com` DNS to our server IP and create HTTPS certificates by runnining the `certbot` command (or whatever else you use).

You could also try provide Gunicorn with your website's HTTPS certificate with the flags `--certfile=cert.pem --keyfile=key.key`. If you use certbot for SSL, your keys are probably in `/etc/letsencrypt/live/`.
