FROM python:3.11

WORKDIR /script

ADD requirments.txt .
ADD src/* src

RUN pip install -r requirments.txt

CMD ["ls"]

CMD ["ls script"]

CMD ["ls script/src"]


CMD ["python", "src/tg_main.py"]