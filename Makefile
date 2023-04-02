build:
	docker build -t certbot-renew .

run:
	docker run --privileged -v "$(PWD)/creds.yaml:/app/creds.yaml" -v "/etc/letsencrypt:/etc/letsencrypt" --rm --name certbot-renew certbot-renew python3 renew.py $(domain) $(dns_propagation_delay)