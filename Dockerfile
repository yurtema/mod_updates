FROM python:3.11

ADD requirments.txt .
ADD src .

RUN pip install -r requerments.txt

CMD ['python', './main.py']