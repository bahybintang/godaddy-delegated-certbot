# (Hacky) Certbot GoDaddy DNS Auto Renew

This script utilizes Selenium to do automation for `certbot` GoDaddy DNS-01 challenge. For automating renewal/creation of SSL certificates, you can wrap this script.

## How to Run

How to:
- Fill in creds in creds.yaml
- Run

```bash
# python3 renew.py domain dns_propagation_delay_in_seconds

python3 renew.py byeol.my.id 120
```

## How to Install (on Debian)

Requirements:
- Python3
- Chrome (Ver 76)
- XVfb
- Dependencies: requirements.txt

```bash
# This script needs to run selenium with chrome WebDriver
# So Chrome is necessary for this to run

curl -L -o chrome.deb "https://www.slimjet.com/chrome/download-chrome.php?file=files%2F76.0.3809.100%2Fgoogle-chrome-stable_current_amd64.deb"
dpkg -i chrome.deb
apt install xvfb
apt install python3
apt install python3-pip
pip install -r requirements.txt
```