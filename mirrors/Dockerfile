FROM python:3.11-alpine

ADD requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

WORKDIR /app

EXPOSE 8080

CMD ["python", "server.py"]


