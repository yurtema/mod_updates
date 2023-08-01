FROM python:3.11

RUN mkdir script

VOLUME ["script/data"]

ADD requirements.txt .
ADD src script/src

RUN pip install -r requirements.txt

WORKDIR /script/src

CMD ["python", "tg_main.py"]