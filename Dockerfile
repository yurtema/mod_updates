FROM python:3.11

WORKDIR /script

ADD requirments.txt .
ADD src/* src

RUN pip install -r requirments.txt


CMD ["python", "src/tg_main.py"]