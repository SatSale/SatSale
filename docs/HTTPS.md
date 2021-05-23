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
You can now point your domain `btcpyment.YOUR.DOMAIN` DNS A Record to your server IP, then create HTTPS certificates using Certbot and Nginx. If you haven't already, can go ahead and install Certbot and run this same command on your primary domain address as well, just change `btcpyment.your.domain` to `your.domain` in the command.
Complete the interactive script and you should receive SSL certificates as long as your DNS records are proper.
```
sudo apt-get update
sudo apt install python3-certbot-nginx
sudo certbot --nginx -d satsale.your.domain
```
