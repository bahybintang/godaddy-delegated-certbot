FROM ubuntu:20.04

LABEL maintainer="bahybintang@gmail.com"

ARG DEBIAN_FRONTEND=noninteractive

ENV TERM=xterm

WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY renew.py /app/renew.py

RUN apt-get update \
    && apt install -y curl \
    && apt-get install -y xvfb \
    && apt-get install -y python3.10 \
    && apt-get install -y python3-pip \
    && pip3 install -r requirements.txt

RUN curl -L -o chrome.deb "https://www.slimjet.com/chrome/download-chrome.php?file=files%2F76.0.3809.100%2Fgoogle-chrome-stable_current_amd64.deb" \
    && apt-get install -y ./chrome.deb \
    && apt-get --fix-broken install -y

RUN pip3 install certbot