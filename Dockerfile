FROM python:3.11

ADD requirments.txt .
ADD src .

RUN pip install -r requirments.txt

CMD ["python", "src/tg_main.py"]