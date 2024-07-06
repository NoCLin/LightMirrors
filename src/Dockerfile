FROM python:3.11-alpine

RUN mkdir -p /wwwroot
WORKDIR /wwwroot

ADD https://github.com/mayswind/AriaNg/releases/download/1.3.7/AriaNg-1.3.7.zip /wwwroot/

RUN unzip AriaNg-1.3.7.zip && rm AriaNg-1.3.7.zip

ADD requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

ADD . /app

WORKDIR /app

EXPOSE 8080

CMD ["python", "mirrorsrun/server.py"]


