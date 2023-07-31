FROM python:3.11

RUN mkdir script

VOLUME ["script/data"]

ADD requirments.txt .
ADD src script/src

RUN pip install -r requirments.txt

WORKDIR /script/src

CMD ["python", "tg_main.py"]